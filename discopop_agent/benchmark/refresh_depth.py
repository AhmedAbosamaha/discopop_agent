"""
Fast refresh vs. full profiling, over a chain of successive rewrites
-------------------------------------------------------------------------------
`test_features.check_fast_refresh_equivalence` asks the question once: after ONE
rewrite, does a refresh reach the same conclusions as a full re-profile?  This
asks it repeatedly, because the agent refreshes repeatedly — every Tier-2 patch
accepted at the same depth triggers another refresh on top of the last one, and
a translation that is sound in one step can still decay when it is chained.

Three arms run over the same sequence of source states, so at every step all
three are looking at byte-identical code:

  full          compile -> run the instrumented binary -> explore.  Ground truth.
  fast-step     one fast refresh applied to the FULL arm's previous profile.
                Isolates the translation itself: any divergence here is a
                single-step error, with nothing accumulated behind it.
  fast-chain    a fast refresh applied to the previous fast refresh, as the
                agent actually does within a depth.  Divergence that shows up
                here but not in fast-step is accumulation.

What is compared, in descending order of what it means:

  patterns      what DiscoPoP CONCLUDES — kind, lines, applicability, pragma
                text.  This is the contract: everything the agent decides is
                downstream of it, so an identical pattern set means the refresh
                did the job whatever happened underneath.
  suggestions   the applicable patterns alone, split into safe and unsafe
                divergence.  A pattern the fast arm calls applicable and the
                full arm does not is the ONLY dangerous class — it is the shape
                of "the refresh lost a dependence and now the code looks
                parallel".  The reverse is over-caution and costs only work.
  dependences   the observed dependence edges, canonicalised.  Explains any
                divergence above, and quantifies carriage when there is none.

Memory-region ids are NOT comparable across builds — the runtime ones are
addresses and the static ones are per-compile hashes — so edges are compared on
(sink, type, source, variable) with the region stripped.  Instruction ids ARE
deterministic for identical source, which is what makes the comparison exact;
`--self-check` verifies that assumption before trusting any of it.

Run it from the repository root:

    venv/bin/python -m discopop_agent.benchmark.refresh_depth
    venv/bin/python -m discopop_agent.benchmark.refresh_depth --case stencil_war
    venv/bin/python -m discopop_agent.benchmark.refresh_depth --depth 2 --keep
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

_HERE = Path(__file__).resolve().parent
_CASES = _HERE / "cases"

# One rewrite step is a list of (old, new) literal replacements, applied in
# order.  Literal rather than regex so a step that no longer matches the case is
# reported as such instead of silently rewriting the wrong thing.
Step = List[Tuple[str, str]]

_KERNEL_FN = """static double kernel(double x) {
    for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
    return x;
}

int main() {"""

# The chains deliberately cover the four edit shapes an LLM rewrite actually
# takes, because each stresses a different part of the translation:
#   storage change      new arrays, new instruction ids interleaved with old
#   block wrap          re-indentation only — the case that used to lose 13/16
#   loop fission        one region becomes two, trip counts must follow
#   function extraction the heaviest renumbering there is
_CHAINS: Dict[str, List[Step]] = {
    "stencil_war": [
        # 1. double-buffer: the rewrite the case exists to provoke.
        [("""    for (int s = 0; s < SWEEPS; s++) {
        for (int i = 0; i < N - 1; i++) {
            double x = 0.5 * (a[i] + a[i + 1]);
            for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
            a[i] = x;
        }
    }
""", """    static double b[N];
    for (int s = 0; s < SWEEPS; s++) {
        for (int i = 0; i < N - 1; i++) {
            double x = 0.5 * (a[i] + a[i + 1]);
            for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
            b[i] = x;
        }
        b[N - 1] = a[N - 1];
        for (int i = 0; i < N; i++) a[i] = b[i];
    }
""")],
        # 2. block wrap: every line inside moves right by four columns.
        [("""        for (int i = 0; i < N - 1; i++) {
            double x = 0.5 * (a[i] + a[i + 1]);
            for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
            b[i] = x;
        }
""", """        if (N > 1) {
            for (int i = 0; i < N - 1; i++) {
                double x = 0.5 * (a[i] + a[i + 1]);
                for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
                b[i] = x;
            }
        }
""")],
        # 3. function extraction: the inner chain leaves main entirely.
        [("int main() {", _KERNEL_FN),
         ("""                double x = 0.5 * (a[i] + a[i + 1]);
                for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
                b[i] = x;
""", """                b[i] = kernel(0.5 * (a[i] + a[i + 1]));
""")],
    ],
    "array_accumulator": [
        # 1. scalarise the accumulator hidden in acc[0].
        [("""    for (int i = 0; i < N; i++) {
        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        out[i] = x;
        acc[0] += (long long)(x * 1000.0);
    }
""", """    long long sum = 0;
    for (int i = 0; i < N; i++) {
        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        out[i] = x;
        sum += (long long)(x * 1000.0);
    }
    acc[0] = sum;
""")],
        # 2. fission: the reduction splits off into its own loop.
        [("""        out[i] = x;
        sum += (long long)(x * 1000.0);
    }
    acc[0] = sum;
""", """        out[i] = x;
    }
    for (int i = 0; i < N; i++) sum += (long long)(out[i] * 1000.0);
    acc[0] = sum;
""")],
        # 3. guard + re-indent the compute loop.
        [("""    for (int i = 0; i < N; i++) {
        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        out[i] = x;
    }
""", """    if (N > 0) {
        for (int i = 0; i < N; i++) {
            double x = a[i];
            for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
            out[i] = x;
        }
    }
""")],
    ],
    "prefix_sum": [
        # 1. fission the recurrence away from the independent work.
        [("""    long long running = 0;
    for (int i = 0; i < N; i++) {
        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        running += (long long)(x * 1000.0);
        out[i] = running;
    }
""", """    static long long contrib[N];
    for (int i = 0; i < N; i++) {
        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        contrib[i] = (long long)(x * 1000.0);
    }
    long long running = 0;
    for (int i = 0; i < N; i++) {
        running += contrib[i];
        out[i] = running;
    }
""")],
        # 2. function extraction out of the now-parallel phase.
        [("int main() {", _KERNEL_FN),
         ("""        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        contrib[i] = (long long)(x * 1000.0);
""", """        contrib[i] = (long long)(kernel(a[i]) * 1000.0);
""")],
        # 3. guard + re-indent the scan.
        [("""    for (int i = 0; i < N; i++) {
        running += contrib[i];
        out[i] = running;
    }
""", """    if (N > 0) {
        for (int i = 0; i < N; i++) {
            running += contrib[i];
            out[i] = running;
        }
    }
""")],
    ],
}


# ---------------------------------------------------------------------------
# Running DiscoPoP
# ---------------------------------------------------------------------------

def _venv_bin(name: str) -> str:
    return str(Path(sys.executable).parent / name)


def _env() -> Dict[str, str]:
    import os
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + ":" + env.get("PATH", "")
    return env


def _run(cmd: Sequence[str], cwd: Path, timeout: int = 1800) -> Tuple[bool, str]:
    try:
        r = subprocess.run(list(cmd), cwd=cwd, env=_env(), capture_output=True,
                           text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)
    return r.returncode == 0, (r.stderr or r.stdout or "")


def _full_profile(work: Path, src: str = "s.cpp") -> Tuple[bool, str]:
    """Compile, RUN the instrumented binary, explore.  The ground truth arm.

    The profiler directory is emptied first, exactly as production now does.
    `discopop_cxx` APPENDS to every artifact and never truncates, so profiling
    twice in one directory merges two copies of the analysis — measured on an
    UNCHANGED source, Data.xml went 444 -> 888 -> 1332 lines over three runs.
    This arm profiles once per step in the same directory, so without the clear
    the ground truth was inflating with every step and every number compared
    against it was wrong.
    """
    shutil.rmtree(work / ".discopop" / "profiler", ignore_errors=True)
    ok, err = _run([_venv_bin("discopop_cxx"), src, "-o", "a.out"], work)
    if not ok:
        return False, f"discopop_cxx: {err[-300:]}"
    ok, err = _run(["./a.out"], work)
    if not ok:
        return False, f"instrumented run: {err[-300:]}"
    ok, err = _run([_venv_bin("discopop_explorer")], work / ".discopop")
    if not ok:
        return False, f"explorer: {err[-300:]}"
    return True, ""


def _fast_refresh(work: Path, old_text: str, new_text: str) -> Tuple[bool, str]:
    """The agent's own fast path, called exactly as phase_a calls it."""
    from ..profiling.runner import _reprofil_fast
    scratch = work / "_refresh"
    scratch.mkdir(exist_ok=True)
    return _reprofil_fast(str(work / "s.cpp"), work / ".discopop",
                          old_text, new_text, scratch)


# ---------------------------------------------------------------------------
# Reading what DiscoPoP concluded
# ---------------------------------------------------------------------------

Pattern = Tuple[str, str, str, bool, str]


def _patterns(dp: Path) -> Optional[List[Pattern]]:
    """Every pattern DiscoPoP emitted: kind, extent, applicability, pragma."""
    f = dp / "explorer" / "patterns.json"
    if not f.exists():
        return None
    raw = json.loads(f.read_text())
    out: List[Pattern] = []
    for kind, entries in raw.get("patterns", {}).items():
        for e in entries or []:
            out.append((kind, str(e.get("start_line")), str(e.get("end_line")),
                        bool(e.get("applicable_pattern")),
                        (e.get("pragma") or "").strip()))
    return sorted(out)


def _applicable(pats: Sequence[Pattern]) -> Set[Tuple[str, str, str]]:
    """The subset the agent would actually act on."""
    return {(k, s, e) for k, s, e, ok, _ in pats if ok}


# A dependence payload is `<var>(<region>)`.  The region is an address at
# runtime and a per-compile hash when static, so neither survives a rebuild —
# see the module docstring.
_REGION = re.compile(r"\(([^()]*)\)$")

Edge = Tuple[str, str, str, str]        # sink, type, source, variable


def _edges(profiler: Path) -> Set[Edge]:
    """Canonical observed dependence edges, region ids stripped.

    Every NOM row counts, including the ones written with a BARE instruction id.
    Those were excluded here as "static dependences regenerated by every
    compile".  They are not: measured on prefix_sum they share ZERO rows with
    static_dependencies.txt, sit in a different instruction-id range, and exist
    only after the binary has run — 42 of the 52 observed rows.  Excluding them
    left this metric blind to 80% of the data, which is why it reported
    `missing=0` for a refresh that had misplaced the `running` recurrence.
    """
    f = profiler / "dynamic_dependencies.txt"
    if not f.exists():
        return set()
    out: Set[Edge] = set()
    for line in f.read_text().splitlines():
        fields = line.split()
        if len(fields) < 4 or fields[1] != "NOM":
            continue
        sink = fields[0]
        i = 2
        while i + 1 < len(fields) + 1 and i < len(fields):
            dep_type = fields[i]
            if i + 1 >= len(fields):
                break
            payload = fields[i + 1]
            i += 2
            if "|" not in payload:
                continue
            source, _, var = payload.partition("|")
            out.add((sink, dep_type, source, _REGION.sub("", var)))
    return out


def _loop_counts(profiler: Path) -> Dict[str, str]:
    f = profiler / "loop_counter_output.txt"
    if not f.exists():
        return {}
    counts: Dict[str, str] = {}
    for line in f.read_text().splitlines():
        fields = line.split()
        if len(fields) >= 3:
            counts[f"{fields[0]}:{fields[1]}"] = fields[2]
    return counts


# ---------------------------------------------------------------------------
# One comparison
# ---------------------------------------------------------------------------

@dataclass
class Comparison:
    case: str
    depth: int
    arm: str
    status: str                      # "match" | "diverged" | "error"
    detail: str = ""
    n_patterns_full: int = 0
    n_patterns_arm: int = 0
    only_full: List[Pattern] = field(default_factory=list)
    only_arm: List[Pattern] = field(default_factory=list)
    unsafe: List[Tuple[str, str, str]] = field(default_factory=list)
    cautious: List[Tuple[str, str, str]] = field(default_factory=list)
    edges_full: int = 0
    edges_arm: int = 0
    edges_missing: int = 0           # observed by the run, absent after refresh
    edges_extra: int = 0             # present after refresh, never observed
    loops_full: int = 0
    loops_arm: int = 0
    loops_missing: int = 0           # a loop the rewrite created: never measured
    loops_wrong: int = 0             # carried forward, but no longer the truth
    note: str = ""
    seconds: float = 0.0


def _compare(case: str, depth: int, arm: str, full: Path, other: Path,
             note: str, seconds: float) -> Comparison:
    c = Comparison(case=case, depth=depth, arm=arm, status="match",
                   note=note, seconds=seconds)

    fp, op = _patterns(full / ".discopop"), _patterns(other / ".discopop")
    if fp is None or op is None:
        c.status = "error"
        c.detail = "no patterns.json from " + ("full" if fp is None else arm)
        return c
    c.n_patterns_full, c.n_patterns_arm = len(fp), len(op)
    c.only_full = sorted(set(fp) - set(op))
    c.only_arm = sorted(set(op) - set(fp))

    # The two directions are not symmetric in what they cost, so they are never
    # reported as one number: a suggestion only the refresh makes is a claim the
    # measured data does not support, and that is the failure that matters.
    af, ao = _applicable(fp), _applicable(op)
    c.unsafe = sorted(ao - af)
    c.cautious = sorted(af - ao)

    ef, eo = _edges(full / ".discopop" / "profiler"), _edges(other / ".discopop" / "profiler")
    c.edges_full, c.edges_arm = len(ef), len(eo)
    c.edges_missing, c.edges_extra = len(ef - eo), len(eo - ef)

    lf, lo = _loop_counts(full / ".discopop" / "profiler"), _loop_counts(other / ".discopop" / "profiler")
    c.loops_full, c.loops_arm = len(lf), len(lo)
    c.loops_missing = sum(1 for k in lf if k not in lo)
    c.loops_wrong = sum(1 for k, v in lo.items() if k in lf and lf[k] != v)

    if c.only_full or c.only_arm:
        c.status = "diverged"
        bits = []
        if c.unsafe:
            bits.append(f"{len(c.unsafe)} UNSAFE (suggested only after refresh: "
                        f"{c.unsafe[:2]})")
        if c.cautious:
            bits.append(f"{len(c.cautious)} lost (suggested only by the full "
                        f"profile: {c.cautious[:2]})")
        if not bits:
            bits.append(f"{len(c.only_full)} only-full / {len(c.only_arm)} "
                        f"only-refresh, none of them applicable")
        c.detail = "; ".join(bits)
    else:
        c.detail = f"identical conclusions ({len(fp)} patterns, {len(af)} applicable)"
    # Trip counts are reported but do NOT decide the verdict.  A count the
    # refresh could not carry is a loop the rewrite created, which no
    # translation could know; a count it carried that no longer matches is
    # staleness the explorer may or may not act on.  Both are worth seeing;
    # neither is the contract, which is what DiscoPoP concludes.
    return c


# ---------------------------------------------------------------------------
# The chain
# ---------------------------------------------------------------------------

def _apply(text: str, step: Step) -> Optional[str]:
    for old, new in step:
        if old not in text:
            return None
        text = text.replace(old, new, 1)
    return text


def run_case(case: str, steps: List[Step], root: Path,
             arms: Sequence[str]) -> List[Comparison]:
    """Drive one case to `len(steps)` depth on every arm and compare each step."""
    out: List[Comparison] = []
    src0 = (_CASES / f"{case}.cpp").read_text()

    dirs = {"full": root / f"{case}_full"}
    if "fast-step" in arms:
        dirs["fast-step"] = root / f"{case}_faststep"
    if "fast-chain" in arms:
        dirs["fast-chain"] = root / f"{case}_fastchain"
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
        (d / "s.cpp").write_text(src0)

    # Depth 0: every arm starts from its own full profile of identical source,
    # so any divergence later is the refresh and nothing else.
    print(f"\n  ── {case} ──")
    for name, d in dirs.items():
        t0 = time.time()
        ok, err = _full_profile(d)
        if not ok:
            out.append(Comparison(case, 0, name, "error", f"baseline: {err}"))
            return out
        print(f"     depth 0  {name:<10} full profile  {time.time() - t0:5.1f}s")

    prev_text = src0
    for depth, step in enumerate(steps, start=1):
        new_text = _apply(prev_text, step)
        if new_text is None:
            out.append(Comparison(case, depth, "-", "error",
                                  "the rewrite no longer matches the case"))
            return out

        # The full arm's profile BEFORE this rewrite is what fast-step starts
        # from, so it has to be taken before the full arm moves on.
        if "fast-step" in dirs:
            snap = dirs["fast-step"]
            shutil.rmtree(snap / ".discopop", ignore_errors=True)
            shutil.copytree(dirs["full"] / ".discopop", snap / ".discopop")
            # FileMapping.txt holds ABSOLUTE paths.  Left pointing at the full
            # arm's copy, the next compile registers this arm's source as a
            # SECOND file id, and every line moves from `1:x` to `2:x` — which
            # looks exactly like a translation failure and is not one.
            fm = snap / ".discopop" / "FileMapping.txt"
            fm.write_text(fm.read_text().replace(
                str((dirs["full"] / "s.cpp").resolve()),
                str((snap / "s.cpp").resolve())))
            (snap / "s.cpp").write_text(prev_text)

        for name, d in dirs.items():
            (d / "s.cpp").write_text(new_text)

        t0 = time.time()
        ok, err = _full_profile(dirs["full"])
        full_secs = time.time() - t0
        if not ok:
            out.append(Comparison(case, depth, "full", "error", err))
            return out
        print(f"     depth {depth}  {'full':<10} full profile  {full_secs:5.1f}s")

        for name in ("fast-step", "fast-chain"):
            if name not in dirs:
                continue
            t0 = time.time()
            ok, note = _fast_refresh(dirs[name], prev_text, new_text)
            secs = time.time() - t0
            if not ok:
                out.append(Comparison(case, depth, name, "error",
                                      f"refresh refused: {note}", seconds=secs))
                continue
            print(f"     depth {depth}  {name:<10} refresh       {secs:5.1f}s"
                  f"  ({full_secs / secs:.1f}x faster)")
            c = _compare(case, depth, name, dirs["full"], dirs[name], note, secs)
            c.detail += f" [full {full_secs:.1f}s vs {secs:.1f}s]"
            out.append(c)

        prev_text = new_text
    return out


def self_check(root: Path) -> bool:
    """Two independent full profiles of identical source must agree.

    The comparison compares instruction ids across separate builds.  If those
    were not deterministic the whole report would be noise, so it is measured
    rather than assumed.
    """
    print("\n  Self-check: are two full profiles of the same source comparable?")
    src = (_CASES / "doall_clean.cpp").read_text()
    a, b = root / "_self_a", root / "_self_b"
    for d in (a, b):
        d.mkdir(parents=True, exist_ok=True)
        (d / "s.cpp").write_text(src)
        ok, err = _full_profile(d)
        if not ok:
            print(f"     SKIP — {err}")
            return False
    pa, pb = _patterns(a / ".discopop"), _patterns(b / ".discopop")
    ea, eb = _edges(a / ".discopop" / "profiler"), _edges(b / ".discopop" / "profiler")
    ok = pa == pb and ea == eb
    print(f"     {'ok' if ok else 'FAIL'} — {len(ea)} edges, {len(pa or [])} patterns, "
          f"{len(ea ^ eb)} edge(s) and {len(set(pa or []) ^ set(pb or []))} pattern(s) "
          f"differ between two runs of the SAME code")
    return ok


def main() -> int:
    p = argparse.ArgumentParser(
        description="Compare fast refresh against full profiling over successive rewrites")
    p.add_argument("--case", nargs="*", default=None,
                   help=f"subset of: {', '.join(_CHAINS)}")
    p.add_argument("--depth", type=int, default=3,
                   help="how many successive rewrites to chain (default 3)")
    p.add_argument("--arms", nargs="*", default=["fast-step", "fast-chain"],
                   choices=["fast-step", "fast-chain"])
    p.add_argument("--json", type=str, default=None, help="write the full result here")
    p.add_argument("--keep", action="store_true", help="keep the working directories")
    a = p.parse_args()

    root = Path(tempfile.mkdtemp(prefix="dp_refresh_depth_"))
    print(f"\n  Fast refresh vs full profiling — working in {root}")

    comparable = self_check(root)
    results: List[Comparison] = []
    for case, steps in _CHAINS.items():
        if a.case and case not in a.case:
            continue
        try:
            results += run_case(case, steps[:a.depth], root, a.arms)
        except Exception as e:                    # noqa: BLE001 - reported, not raised
            results.append(Comparison(case, -1, "-", "error", f"{type(e).__name__}: {e}"))

    print("\n  ── results ──\n")
    hdr = f"  {'case':<18}{'depth':>6}  {'arm':<11}{'verdict':<10} detail"
    print(hdr)
    print("  " + "-" * (len(hdr) - 2))
    for c in results:
        mark = {"match": "  ok  ", "diverged": " DIFF ", "error": " ERR  "}[c.status]
        print(f"  {c.case:<18}{c.depth:>6}  {c.arm:<11}[{mark}] {c.detail}")
        if c.status != "error":
            print(f"  {'':<18}{'':>6}  {'':<11}         "
                  f"deps: {c.edges_arm} vs {c.edges_full} measured, "
                  f"{c.edges_missing} missing, {c.edges_extra} extra")
            print(f"  {'':<18}{'':>6}  {'':<11}         "
                  f"trip counts: {c.loops_arm} vs {c.loops_full}, "
                  f"{c.loops_missing} missing, {c.loops_wrong} stale")
            print(f"  {'':<18}{'':>6}  {'':<11}         {c.note}")

    matched = sum(1 for c in results if c.status == "match")
    diverged = [c for c in results if c.status == "diverged"]
    errors = [c for c in results if c.status == "error"]
    unsafe = [c for c in diverged if c.unsafe]
    print(f"\n  {matched} matched, {len(diverged)} diverged, {len(errors)} errored")
    if unsafe:
        print(f"  {len(unsafe)} comparison(s) produced a suggestion the measured "
              f"profile does NOT support — these are the ones that matter")
    stale = [c for c in results if c.loops_wrong or c.loops_missing]
    if stale:
        print(f"  {len(stale)} comparison(s) carried a loop trip count that is "
              f"missing or no longer the measured value — see the trip-count rows")
    if not comparable:
        print("  (self-check did not pass: treat the above as indicative only)")

    if a.json:
        Path(a.json).write_text(json.dumps(
            [c.__dict__ for c in results], indent=2, default=str))
        print(f"  full result written to {a.json}")

    if not a.keep:
        shutil.rmtree(root, ignore_errors=True)
    else:
        print(f"  working directories kept in {root}")
    return 1 if (diverged or errors) else 0


if __name__ == "__main__":
    sys.exit(main())
