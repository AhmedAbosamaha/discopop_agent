"""
Feature regression suite — verifies the agent's machinery without an LLM
------------------------------------------------------------------------
The existing benchmark (`benchmark/run.py`) measures how well a MODEL does on
parallelization cases: it needs an API key, takes minutes, and its results move
with the model.  This suite is the other half — it checks the parts of the agent
that are supposed to be deterministic, and it must pass on every commit:

  * impact ranking    the queue is ordered by measured time, not instruction count
  * min-impact        a region too small to pay off is dropped before any LLM call
  * hotspot remap     runtime measurements follow the code, or are dropped
  * mixed-scale rank  a measured region outranks one scored only by the proxy
  * fast refresh      an edit that changes nothing loses no dependence data,
                      and a refresh reaches the same conclusions as a full re-profile
  * reduction carry   a refresh keeps the measured reductions — the one thing it
                      can drop that makes the agent LESS cautious, not more
  * clause checks     the pragma defects that compile, run and print the right answer
  * dep review        a discharged blocker actually removes dependence lines
  * TSan barrier      a real race is caught; an artefact of the OpenMP runtime is not
  * equivalence       reordered arithmetic is accepted, everything else rejected
  * noise floor       a float reduction measures slack, an integer program none
  * schedule stress   a race fails on repeatability, a correct reduction survives
  * dep evidence      a real recurrence is contradicted; unprofiled code says so
  * dep lines         a dependence is attributed to the line it is really on

Run it from the repository root:

    venv/bin/python -m discopop_agent.benchmark.test_features
    venv/bin/python -m discopop_agent.benchmark.test_features --only clause tsan

Checks that need tooling which is not installed (DiscoPoP, clang, libarcher)
report SKIP rather than failing, so the suite is useful on a partial setup.
"""
from __future__ import annotations

import argparse
import os
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from ..profiling.fast_refresh import (line_map, remap_dependencies,
                                      remap_reduction, verify_translation)
from ..plan.impact import load_hotspots
from ..plan import build_candidates
from ..types import EvidencePackage, HotspotCandidate
from ..llm import make_diff
from ..gate.toolchain import _find_clangpp, _macos_sysroot_flag, find_archer

_HERE = Path(__file__).resolve().parent
_CASES = _HERE / "cases"
_REPO = _HERE.parent.parent


@dataclass
class Result:
    name: str
    status: str          # "pass" | "fail" | "skip"
    detail: str = ""


def _venv_bin(name: str) -> str:
    return str(Path(sys.executable).parent / name)


def _env() -> Dict[str, str]:
    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    env["PYTHONPATH"] = str(_REPO) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def _run(cmd: List[str], cwd: Path, timeout: int = 900) -> Tuple[bool, str]:
    try:
        r = subprocess.run(cmd, cwd=cwd, env=_env(), capture_output=True,
                           text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as e:
        return False, str(e)
    return r.returncode == 0, (r.stderr or r.stdout or "")


def _profile(work: Path, src_name: str, hotspots: bool = True,
             c_as_c: bool = False) -> Tuple[bool, str]:
    """Dependence profile, and optionally the hotspot measurement beside it.

    Clears the profiler directory first, as production does: discopop_cxx
    appends to every artifact it writes, so profiling the same directory twice
    merges two copies of the analysis (Data.xml 444 -> 888 -> 1332 lines over
    three runs of ONE unchanged source).  Any check here that profiles twice was
    comparing against an inflated baseline.
    """
    shutil.rmtree(work / ".discopop" / "profiler", ignore_errors=True)
    wrapper = "discopop_cc" if c_as_c and src_name.endswith(".c") else "discopop_cxx"
    ok, err = _run([_venv_bin(wrapper), src_name, "-o", "a.out"], work)
    if not ok:
        return False, f"{wrapper}: {err[-200:]}"
    ok, err = _run(["./a.out"], work)
    if not ok:
        return False, f"profiled run: {err[-200:]}"
    ok, err = _run([_venv_bin("discopop_explorer")], work / ".discopop")
    if not ok:
        return False, f"explorer: {err[-200:]}"
    if hotspots:
        ok, err = _run([_venv_bin("discopop_hotspot_cxx"), src_name, "-o", "hs.out"], work)
        if not ok:
            return False, f"discopop_hotspot_cxx: {err[-200:]}"
        ok, err = _run(["./hs.out"], work)
        if not ok:
            return False, f"hotspot run: {err[-200:]}"
        ok, err = _run([_venv_bin("discopop_hotspot_analyzer")], work / ".discopop")
        if not ok:
            return False, f"hotspot analyzer: {err[-200:]}"
    return True, ""


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_impact_ranking(work: Path) -> Result:
    """The hot loop must outrank the cold one, whatever the instruction counts say.

    `priority_mix.cpp` is built for exactly this: a 4,000,000-iteration integer
    loop that costs almost nothing, and a 2,000-iteration floating-point chain
    that costs almost everything.  The workload proxy ranks a 0.1 ms checksum
    loop FIRST on this program; the measured ranking must not.
    """
    src = "priority_mix.cpp"
    shutil.copy(_CASES / src, work / src)
    ok, err = _profile(work, src)
    if not ok:
        return Result("impact ranking", "skip", err)

    dp = work / ".discopop"
    model = load_hotspots(dp, threads=8)
    if not model.available:
        return Result("impact ranking", "skip", "no hotspot measurements produced")

    ranked = build_candidates(dp, str(work / src), 1.0, 0.0,
                              impact=model, min_impact=0.0)
    if not ranked:
        return Result("impact ranking", "fail", "no candidates at all")
    top = ranked[0]
    frac = top.runtime_fraction or 0.0
    if frac < 0.5:
        order = ", ".join(f"{c.region.region_id}@{(c.runtime_fraction or 0)*100:.0f}%"
                          for c in ranked[:4])
        return Result("impact ranking", "fail",
                      f"top candidate holds only {frac*100:.1f}% of runtime ({order})")

    # And the cold region must not be ahead of the hot one.
    cold = [c for c in ranked if (c.runtime_fraction or 1.0) < 0.05]
    if cold and ranked.index(cold[0]) < ranked.index(top):
        return Result("impact ranking", "fail", "a cold region outranked the hot one")
    return Result("impact ranking", "pass",
                  f"top = {top.region.region_id} at {frac*100:.1f}% of runtime, "
                  f"{len(cold)} cold region(s) ranked below it")


def check_min_impact(work: Path) -> Result:
    """--min-impact must drop regions that cannot pay for themselves."""
    dp = work / ".discopop"
    src = str(work / "priority_mix.cpp")
    if not (dp / "hotspot_detection" / "Hotspots.json").exists():
        return Result("min-impact filter", "skip", "needs the impact-ranking profile")
    model = load_hotspots(dp, threads=8)
    everything = build_candidates(dp, src, 1.0, 0.0, impact=model, min_impact=0.0)
    hot_only = build_candidates(dp, src, 1.0, 0.0, impact=model, min_impact=0.05)
    if len(hot_only) >= len(everything):
        return Result("min-impact filter", "fail",
                      f"a 50 ms floor removed nothing ({len(everything)} candidates)")
    if not hot_only:
        return Result("min-impact filter", "fail", "a 50 ms floor removed everything")
    smallest = min((c.impact_seconds or 0.0) for c in hot_only)
    if smallest < 0.05:
        return Result("min-impact filter", "fail",
                      f"kept a region predicted to save {smallest*1e3:.1f} ms")
    return Result("min-impact filter", "pass",
                  f"{len(everything)} → {len(hot_only)} candidates at a 50 ms floor")


def check_fast_refresh(work: Path) -> Result:
    """A semantically empty edit must carry every observed dependence forward.

    This is the property that makes the translation trustworthy: if nothing
    changed, nothing may be lost.  A real rewrite legitimately drops the
    dependences belonging to code it deleted, so only the identity case can
    assert losslessness.
    """
    src_name = "array_accumulator.cpp"
    base = work / "fr_base"
    edited = work / "fr_edited"
    for d in (base, edited):
        d.mkdir(parents=True, exist_ok=True)
    shutil.copy(_CASES / src_name, base / src_name)
    (edited / src_name).write_text(
        "// a semantically empty edit\n" + (base / src_name).read_text()
    )

    ok, err = _profile(base, src_name, hotspots=False)
    if not ok:
        return Result("fast refresh", "skip", err)
    # The edited side only needs the COMPILE — that is the whole point.
    ok, err = _run([_venv_bin("discopop_cxx"), src_name, "-o", "a.out"], edited)
    if not ok:
        return Result("fast refresh", "skip", f"discopop_cxx: {err[-200:]}")

    old_src = (base / src_name).read_text()
    new_src = (edited / src_name).read_text()
    lmap = line_map(old_src, new_src)
    problems = verify_translation(old_src, new_src, lmap)
    if problems:
        return Result("fast refresh", "fail", f"line map self-check: {problems[0]}")

    op = base / ".discopop" / "profiler"
    np_ = edited / ".discopop" / "profiler"
    text, stats = remap_dependencies(
        (op / "dynamic_dependencies.txt").read_text(),
        op / "instructionID_to_lineID_mapping.txt",
        np_ / "instructionID_to_lineID_mapping.txt", lmap,
    )
    if stats.deps_in == 0:
        return Result("fast refresh", "skip", "the profile recorded no dependences")
    if stats.deps_out != stats.deps_in:
        return Result("fast refresh", "fail",
                      f"identity edit lost {stats.deps_in - stats.deps_out} of "
                      f"{stats.deps_in} dependences")
    if stats.loops_out != stats.loops_in:
        return Result("fast refresh", "fail",
                      f"identity edit lost {stats.loops_in - stats.loops_out} trip counts")
    return Result("fast refresh", "pass",
                  f"{stats.deps_out}/{stats.deps_in} dependences and "
                  f"{stats.loops_out}/{stats.loops_in} trip counts carried, lossless")



def check_reduction_carry(work: Path) -> Result:
    """A refresh must carry the measured REDUCTIONS, not only the dependences.

    Losing them is conservative — measured directly: emptying `reduction.txt`
    over an otherwise byte-identical profile makes the `reduction` suggestion
    disappear rather than become an unguarded `do_all`, because the
    loop-carried dependence on the accumulator still blocks Do-All by itself.
    So this guards an opportunity, not a race: every reduction the profiler
    measured was being thrown away, and those loops silently stopped being
    suggested at all.

    It failed silently and totally.  `reduction.txt` is written in a LABELLED
    form — `FileID : 1 Loop Line Number : 17 Reduction Line Number : 21 ...` —
    but the remapper read it as bare `fileID line` columns, so `int(fields[1])`
    was `int(":")` on every line, every line raised, and the file came out
    EMPTY.  Not "empty after a big rewrite": empty after an edit that changed
    nothing at all, which is what this checks.
    """
    src_name = "array_accumulator.cpp"
    base = work / "rc_base"
    base.mkdir(parents=True, exist_ok=True)
    shutil.copy(_CASES / src_name, base / src_name)

    ok, err = _profile(base, src_name, hotspots=False)
    if not ok:
        return Result("reduction carry", "skip", err)

    measured = (base / ".discopop" / "profiler" / "reduction.txt").read_text()
    records = [ln for ln in measured.splitlines() if ln.strip()]
    if not records:
        return Result("reduction carry", "skip",
                      "the profile detected no reduction to carry")

    old_src = (base / src_name).read_text()
    # An edit that shifts every line down by one and changes nothing else: the
    # records must all survive, with both of their line numbers moved.
    new_src = "// a semantically empty edit\n" + old_src
    lmap = line_map(old_src, new_src)
    # The fast refresh no longer calls this: discopop_cxx regenerates
    # reduction.txt correctly for the new source, and overwriting it with a
    # translated stale record cost the array_accumulator rewrite its `reduction`
    # classification (DiscoPoP then reported a plain do_all on an accumulation
    # loop).  The translation itself is still exercised here, and the pinning
    # assertion below is what stops the file being carried again.
    from ..profiling.runner import _COMPILE_ARTIFACTS, _RUN_ARTIFACTS
    if "reduction.txt" in _RUN_ARTIFACTS or "reduction.txt" not in _COMPILE_ARTIFACTS:
        return Result("reduction carry", "fail",
                      "reduction.txt is being carried across a fast refresh again — "
                      "the compile writes it correctly; overwriting it drops the "
                      "reduction classification")
    carried = [ln for ln in remap_reduction(measured, lmap).splitlines() if ln.strip()]

    if len(carried) != len(records):
        return Result("reduction carry", "fail",
                      f"a one-line shift lost {len(records) - len(carried)} of "
                      f"{len(records)} reduction record(s) — the loops they "
                      f"describe become plain do_all, with no reduction clause")

    # Both line numbers move, and they move by the same shift the edit applied.
    import re as _re
    field = _re.compile(r"Loop Line Number : (\d+) Reduction Line Number : (\d+)")
    for before, after in zip(records, carried):
        b, a = field.search(before), field.search(after)
        if b is None or a is None:
            return Result("reduction carry", "fail",
                          f"the carried record no longer parses: {after!r}")
        if (int(a.group(1)), int(a.group(2))) != (int(b.group(1)) + 1, int(b.group(2)) + 1):
            return Result("reduction carry", "fail",
                          f"lines did not follow the shift: {before.strip()!r} "
                          f"-> {after.strip()!r}")
    return Result("reduction carry", "pass",
                  f"reduction.txt left to the compile; translation still correct on "
                  f"{len(carried)}/{len(records)} record(s), "
                  f"both line numbers shifted with the edit")


_CLAUSE_SRC = """#include <cstdio>
int main() {
  static double b[100];
  double a[100];
  int ok = 1;
  for (int i = 0; i < 100; i++) a[i] = i;
  for (int i = 0; i < 100; i++) {
    double x = a[i] * 2;
    b[i] = x;
  }
  for (int i = 0; i < 99; i++) {
    if (b[i] > b[i + 1]) ok = 0;
  }
  printf("%f %d\\n", b[3], ok);
}
"""


def check_clauses(work: Path) -> Result:
    """The clause rules must catch what nothing else can, and only that.

    `private` on a variable the loop writes and later code reads compiles, races
    nowhere and prints the right answer whenever the data happens to agree — so
    only a static read can reject it.  The pointer case is the guard against
    over-rejection.
    """
    from ..pragmas import check_llm_pragmas, check_pragma_clauses
    from ..llm import make_diff

    src = work / "clause_case.cpp"
    src.write_text(_CLAUSE_SRC)
    orig = src.read_text()

    cases: List[Tuple[str, str, bool]] = []
    cases.append((
        "private on a live-out scalar",
        orig.replace("  for (int i = 0; i < 99; i++) {",
                     "  #pragma omp parallel for private(ok)\n  for (int i = 0; i < 99; i++) {"),
        True,
    ))
    cases.append((
        "private on an array the loop fills",
        orig.replace("  for (int i = 0; i < 100; i++) {\n    double x",
                     "  #pragma omp parallel for private(b)\n  for (int i = 0; i < 100; i++) {\n    double x"),
        True,
    ))
    cases.append((
        "private on a body-local",
        orig.replace("  for (int i = 0; i < 100; i++) {\n    double x",
                     "  #pragma omp parallel for private(x)\n  for (int i = 0; i < 100; i++) {\n    double x"),
        True,
    ))
    cases.append((
        "a clean pragma",
        orig.replace("  for (int i = 0; i < 100; i++) a[i] = i;",
                     "  #pragma omp parallel for\n  for (int i = 0; i < 100; i++) a[i] = i;"),
        False,
    ))

    # Four false rejections found in local_obs1 (2mm, jacobi-2d-imper): a counter
    # declared once per function and reused by the NEXT loop nest is not live-out,
    # and neither a later pragma nor a comment reads anything. Each of these
    # refused a correct pragma; the last case must still be rejected.
    reuse = ("void f(int n, double *a) {\n  int i, j;\n"
             "  for (i = 0; i < n; i++)\n    for (j = 0; j < n; j++)\n      a[i*n+j] = 0;\n"
             "%s"
             "  for (i = 0; i < n; i++)\n    for (j = 0; j < n; j++)\n      a[i*n+j] += 1;\n%s}\n")
    head = "  for (i = 0; i < n; i++)\n    for (j = 0; j < n; j++)\n      a[i*n+j] = 0;\n"
    prag = "  #pragma omp parallel for private(j)\n" + head
    for label, text, should_reject in [
        ("counter re-initialised by the next loop", reuse % ("", ""), False),
        ("a later pragma naming the counter",
         reuse % ("  #pragma omp parallel for private(j)\n", ""), False),
        ("a comment mentioning the counter",
         reuse % ("  /* second phase: independent (i,j) iterations */\n", ""), False),
        ("a genuine read after the re-initialising loop",
         reuse % ("", "  a[0] = j;\n"), True),
    ]:
        cases.append((label, text.replace(head, prag, 1), should_reject))

    failures = []
    for label, new_text, should_reject in cases:
        base = orig if label not in {
            "counter re-initialised by the next loop", "a later pragma naming the counter",
            "a comment mentioning the counter", "a genuine read after the re-initialising loop",
        } else new_text.replace(prag, head, 1)
        if base is not orig:
            src.write_text(base)
        problem = check_llm_pragmas(make_diff(base, new_text, str(src)), str(src))
        if base is not orig:
            src.write_text(orig)
        if bool(problem) != should_reject:
            failures.append(f"{label}: expected "
                            f"{'rejection' if should_reject else 'acceptance'}")
    if failures:
        return Result("clause checks", "fail", "; ".join(failures))
    # Two false negatives that both shipped the exact defect this module exists
    # to catch, found by varying only distance and only line breaks:
    #   * the lookahead stopped after a fixed 60 lines, so the same private(ok)
    #     was caught at gap 40 and missed at gap 70;
    #   * a ONE-LINE loop body was dropped wholesale by `body[1:]`, so the write
    #     was never seen at any distance.
    def _sortedness(gap: int, one_line: bool, read_after: bool = True) -> Tuple[str, str]:
        body = ("    for (int i=0;i<99;i++) { if (arr[i] > arr[i+1]) ok = 0; }\n"
                if one_line else
                "    for (int i=0;i<99;i++) {\n"
                "        if (arr[i] > arr[i+1]) ok = 0;\n    }\n")
        pad = "".join(f"    volatile int pad{i} = {i};\n" for i in range(gap))
        tail = ('    printf("sorted: %s\\n", ok ? "YES" : "NO");\n' if read_after
                else '    printf("done\\n");\n')
        text = ("#include <cstdio>\nint main(){\n    int arr[100];\n"
                "    for (int i=0;i<100;i++) arr[i]=i;\n    int ok = 1;\n"
                + body + pad + tail + "    return 0;\n}\n")
        return text, body.splitlines()[0] + "\n"

    scope_dir = work / "clause_scope"
    scope_dir.mkdir(parents=True, exist_ok=True)
    checked = 0
    for one_line in (False, True):
        for gap in (5, 40, 70, 200):
            for read_after in (True, False):
                text, head = _sortedness(gap, one_line, read_after)
                f = scope_dir / f"s_{int(one_line)}_{gap}_{int(read_after)}.cpp"
                f.write_text(text)
                patched = text.replace(head, "    #pragma omp parallel for private(ok)\n" + head)
                got = check_pragma_clauses(make_diff(text, patched, str(f)), str(f))
                want = read_after          # rejected iff the value is read afterwards
                if bool(got) != want:
                    shape = "one-line body" if one_line else "multi-line body"
                    return Result("clause checks", "fail",
                                  f"private(ok), {shape}, read {gap} lines after, "
                                  f"read_after={read_after}: expected "
                                  f"{'rejection' if want else 'acceptance'}, got "
                                  f"{got or 'acceptance'}")
                checked += 1
    # Phase B's repair of DiscoPoP's own clauses (Fix 79): a name declared inside the
    # loop body leaves EVERY clause; names from the enclosing scope are never touched.
    from ..pragmas import _repair_pragma_clauses
    rsrc = ("void f(int n, double* a) {\n  int i, k;\n  double acc = 0.0;\n"
            "  for (i = 0; i < n; i++) {\n    int x = i * 2;\n    double t = a[i];\n"
            "    acc += t * x;\n  }\n}\n")
    rfile = work / "repair.c"
    rfile.write_text(rsrc)
    rdiff = make_diff(rsrc, rsrc.replace("  for (i = 0; i < n; i++) {\n",
        "  #pragma omp parallel for private(x, k) firstprivate(t) shared(a, x) reduction(+:acc, x)\n"
        "  for (i = 0; i < n; i++) {\n", 1), str(rfile))
    repaired = next((l for l in (_repair_pragma_clauses(rdiff, str(rfile)) or "").splitlines()
                     if "pragma" in l), "")
    if "private(k) shared(a) reduction(+:acc)" not in repaired or "firstprivate" in repaired:
        return Result("clause checks", "fail",
                      f"clause repair produced {repaired!r}, want private(k) shared(a) reduction(+:acc)")
    # Fix 91 — a later loop that WRITES the name before reading it does not read the
    # stale value.  `s281` (E1): the loop split at n/2, DiscoPoP's `private(x)` on the
    # first half was refused because the second half mentions `x`.  The three
    # neighbours must still be refused: a write under an `if`, a read before the
    # write, and a read after the later loop (which may run zero times).
    split = ("void f(int n, double *a, double *b, double *c) {\n  double x;\n"
             "  for (int i = 0; i < n / 2; i++) {\n    x = a[n-i-1] + b[i] * c[i];\n"
             "    a[i] = x - 1.0;\n    b[i] = x;\n  }\n"
             "  for (int i = n / 2; i < n; i++) {\n%s    a[i] = x - 1.0;\n    b[i] = x;\n  }\n%s}\n")
    first = "  for (int i = 0; i < n / 2; i++) {\n"
    for label, second, tail, want in [
        ("a later loop that writes the scalar first (s281)", "    x = a[n-i-1] + b[i] * c[i];\n", "", False),
        ("a later loop that writes it only under an if", "    if (b[i] > 0) x = a[n-i-1];\n", "", True),
        ("a later loop that reads it before writing", "    b[i] += x;\n    x = a[n-i-1];\n", "", True),
        ("a read after the later loop", "    x = a[n-i-1] + b[i] * c[i];\n", "  a[0] = x;\n", True),
    ]:
        text = split % (second, tail)
        sfile = scope_dir / "split.c"
        sfile.write_text(text)
        got = check_pragma_clauses(make_diff(text, text.replace(
            first, "  #pragma omp parallel for private(x)\n" + first, 1), str(sfile)), str(sfile))
        if bool(got) != want:
            return Result("clause checks", "fail",
                          f"{label}: expected {'rejection' if want else 'acceptance'}, "
                          f"got {got or 'acceptance'}")
    return Result("clause checks", "pass",
                  f"{len(cases)}/{len(cases)} verdicts correct; "
                  f"{checked} scope cases (distance and one-line bodies) correct")


_TWO_REGIONS = """#include <cstdio>
static const int N = 4096;
int main() {
    static int a[N];
    for (int rep = 0; rep < 200; rep++) {
        #pragma omp parallel for schedule(static, 1)
        for (int i = 0; i < N; i++) a[i] = i + rep;
        #pragma omp parallel for schedule(static, 1)
        for (int i = 0; i < N; i++) a[N - 1 - i] += 1;
    }
    long long s = 0;
    for (int i = 0; i < N; i++) s += a[i];
    printf("sum %lld\\n", s);
    return 0;
}
"""

_REAL_RACE = """#include <cstdio>
#include <cstdlib>
#define N 513
int main() {
    int *arr = (int *)malloc(N * sizeof(int));
    for (int i = 0; i < N; i++) arr[i] = N - i;
    for (int pass = 0; pass < N - 1; pass++) {
        #pragma omp parallel for shared(arr)
        for (int i = 0; i < N - pass - 1; i++) {
            if (arr[i] > arr[i + 1]) { int t = arr[i]; arr[i] = arr[i+1]; arr[i+1] = t; }
        }
    }
    printf("done\\n"); free(arr); return 0;
}
"""


def check_tsan_barrier(work: Path) -> Result:
    """A real race must be reported; two barrier-separated regions must not.

    Without archer, TSan cannot see OpenMP's barriers and calls the second case
    a race too — so this check is what tells you whether the sanitizer on this
    machine is trustworthy, and whether the fallback heuristic agrees with it.
    """
    from ..gate.tsan import _is_omp_barrier_false_positive

    clangpp = _find_clangpp()
    if clangpp is None:
        return Result("TSan barrier", "skip", "no supported clang++ found")

    def build_and_run(name: str, code: str) -> Tuple[bool, str]:
        f = work / f"{name}.cpp"
        f.write_text(code)
        cmd = [clangpp, str(f), *_macos_sysroot_flag(),
               "-fsanitize=thread", "-fopenmp", "-g", "-O1",
               "-L/usr/local/opt/libomp/lib", "-o", str(work / name)]
        ok, err = _run(cmd, work)
        if not ok:
            return False, err[-200:]
        env = _env()
        env["TSAN_OPTIONS"] = "halt_on_error=1"
        env["DYLD_LIBRARY_PATH"] = "/usr/local/opt/libomp/lib"
        archer = find_archer()
        if archer:
            env["OMP_TOOL_LIBRARIES"] = archer
            env["TSAN_OPTIONS"] += ":ignore_noninstrumented_modules=1"
        r = subprocess.run([str(work / name)], cwd=work, env=env,
                           capture_output=True, text=True, timeout=600)
        out = (r.stderr or "") + (r.stdout or "")
        return True, out

    built, safe_out = build_and_run("two_regions", _TWO_REGIONS)
    if not built:
        return Result("TSan barrier", "skip", f"build failed: {safe_out}")
    built, racy_out = build_and_run("real_race", _REAL_RACE)
    if not built:
        return Result("TSan barrier", "skip", f"build failed: {racy_out}")

    racy_reported = "ThreadSanitizer: data race" in racy_out
    safe_reported = "ThreadSanitizer: data race" in safe_out
    archer = find_archer()

    if not racy_reported:
        return Result("TSan barrier", "fail",
                      "a genuine race in one parallel region was NOT reported")
    if not safe_reported:
        return Result("TSan barrier", "pass",
                      f"real race caught, barrier-separated regions clean "
                      f"({'archer active' if archer else 'no archer needed'})")
    # The artefact appeared — the fallback heuristic has to recognise it, and
    # must still not excuse the genuine race.
    if not _is_omp_barrier_false_positive(safe_out, _TWO_REGIONS):
        return Result("TSan barrier", "fail",
                      "barrier artefact reported and the heuristic did not catch it")
    if _is_omp_barrier_false_positive(racy_out, _REAL_RACE):
        return Result("TSan barrier", "fail",
                      "the heuristic excused a GENUINE race")
    return Result("TSan barrier", "pass",
                  "no archer: artefact recognised by the heuristic, real race still caught")


_STENCIL_ORIG = """    for (int s = 0; s < SWEEPS; s++) {
        for (int i = 0; i < N - 1; i++) {
            double x = 0.5 * (a[i] + a[i + 1]);
            for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
            a[i] = x;
        }
    }
"""

_STENCIL_REWRITE = """    static double b[N];
    for (int s = 0; s < SWEEPS; s++) {
        for (int i = 0; i < N - 1; i++) {
            double x = 0.5 * (a[i] + a[i + 1]);
            for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
            b[i] = x;
        }
        b[N - 1] = a[N - 1];
        for (int i = 0; i < N; i++) a[i] = b[i];
    }
"""


def _patterns(dp: Path) -> Optional[List[Tuple[str, str, str, bool, str]]]:
    f = dp / "explorer" / "patterns.json"
    if not f.exists():
        return None
    import json
    raw = json.loads(f.read_text())
    out = []
    for kind, entries in raw.get("patterns", {}).items():
        for e in entries or []:
            out.append((kind, str(e.get("start_line")), str(e.get("end_line")),
                        bool(e.get("applicable_pattern")), (e.get("pragma") or "").strip()))
    return sorted(out)


def check_fast_refresh_equivalence(work: Path) -> Result:
    """A fast refresh must reach the SAME conclusions as a full re-profile.

    Losslessness on an identity edit says the translation preserves data; this
    says the translation preserves MEANING.  The same rewrite is profiled both
    ways and DiscoPoP's patterns are compared — kind, lines, applicability and
    the pragma text.  If a fast refresh ever changes what DiscoPoP concludes,
    every decision downstream of it is standing on different ground.
    """
    base = work / "eq_full"
    fast = work / "eq_fast"
    for d in (base, fast):
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy(_CASES / "stencil_war.cpp", d / "s.cpp")

    for d in (base, fast):
        ok, err = _profile(d, "s.cpp", hotspots=False)
        if not ok:
            return Result("fast refresh ≡ full", "skip", err)

    for d in (base, fast):
        src = d / "s.cpp"
        text = src.read_text()
        if _STENCIL_ORIG not in text:
            return Result("fast refresh ≡ full", "skip", "the case no longer matches")
        (d / "old.cpp").write_text(text)
        src.write_text(text.replace(_STENCIL_ORIG, _STENCIL_REWRITE, 1))

    ok, err = _profile(base, "s.cpp", hotspots=False)          # the full path
    if not ok:
        return Result("fast refresh ≡ full", "skip", err)

    from ..args import AgentArguments
    from ..profiling.runner import _reprofil_fast
    out = fast / "out"
    out.mkdir(exist_ok=True)
    args = AgentArguments(
        discopop_dir=str(fast / ".discopop"), source_file=str(fast / "s.cpp"),
        budget=1, model="haiku", api_key=None, provider="claude-agent-sdk",
        api_base=None, lambda_penalty=1.0, min_workload=0.0, output_dir=str(out),
        dry_run=False, edit_mode="direct", llm_pragmas=True, pragma_arbitration=True, fast_refresh=True,
        llm_deps=False, hotspots=False, min_impact=0.0, restructure_depth=0,
        require_speedup=False, judge_as_shipped=False, requeue_rejected=False, phase_b_reuse_d40=False, build_retries=2, apply_patches=True,
        min_measured_speedup=1.1, check_inputs=[], reprofil_args=[], verbose=False)
    ok, note = _reprofil_fast(args.source_file, Path(args.discopop_dir),
                              (fast / "old.cpp").read_text(),
                              (fast / "s.cpp").read_text(), out)
    if not ok:
        return Result("fast refresh ≡ full", "fail", f"fast refresh failed: {note}")

    full_p = _patterns(base / ".discopop")
    fast_p = _patterns(fast / ".discopop")
    if full_p is None or fast_p is None:
        return Result("fast refresh ≡ full", "skip", "no patterns.json from one side")
    # One divergence is KNOWN and is not a defect.  The double-buffer rewrite
    # touches lines inside the outer sweep loop at 1:19, so the dependences that
    # block it were never observed — the previous run predates that code, and no
    # translation can recover what was never measured.  Verified at the edge
    # level: 26 of 26 dependences the full profile has and the refresh lacks
    # have an endpoint on a rewritten line, and 0 were carryable.  So this one
    # is pinned rather than treated as a failure, and ANY other divergence still
    # fails — that is what keeps the check useful.
    _KNOWN_GAP = {("do_all", "1:19", "1:19")}

    def _key(p: object) -> Tuple[object, ...]:
        return tuple(p[:3]) if isinstance(p, (list, tuple)) else (p,)

    only_full = sorted(set(full_p) - set(fast_p))
    only_fast = sorted(set(fast_p) - set(full_p))
    unexpected_full = [p for p in only_full if _key(p) not in _KNOWN_GAP]
    unexpected_fast = [p for p in only_fast if _key(p) not in _KNOWN_GAP]
    if unexpected_full or unexpected_fast:
        return Result("fast refresh ≡ full", "fail",
                      f"{len(full_p)} vs {len(fast_p)} patterns; unexpected divergence "
                      f"only-full={unexpected_full[:2]} only-fast={unexpected_fast[:2]}")
    if only_full or only_fast:
        return Result("fast refresh ≡ full", "pass",
                      f"{len(full_p)} vs {len(fast_p)} patterns; only the known "
                      f"new-code gap at 1:19 (nothing else diverged) — {note}")
    return Result("fast refresh ≡ full", "pass",
                  f"identical DiscoPoP conclusions ({len(full_p)} patterns) — {note}")


def check_dep_review(work: Path) -> Result:
    """A discharged blocker must actually remove dependence lines.

    The failure this guards against was silent and total: the match key was
    built from the blocker's `sink_line` / `source_line`, which the detector
    writes as the STRING "None", so every verdict matched nothing and the whole
    feature was an expensive no-op.  Nothing looked wrong — the model answered,
    the log said "judged spurious", and the analysis was untouched.

    The model is stubbed to call everything impossible, so this tests the
    plumbing, not any model's judgement.
    """
    src_name = "prefix_sum.cpp"
    d = work / "review"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(_CASES / src_name, d / src_name)
    ok, err = _profile(d, src_name, hotspots=False)
    if not ok:
        return Result("dependence review", "skip", err)

    static = d / ".discopop" / "profiler" / "static_dependencies.txt"
    if not static.exists():
        return Result("dependence review", "skip", "no static_dependencies.txt")
    blockers = d / ".discopop" / "explorer" / "doall_prevented.json"
    import json
    if not blockers.exists() or not json.loads(blockers.read_text()):
        # Not benign, and not this check's fault.  Measured on prefix_sum.cpp:
        # roughly one profile run in six produces 0 blockers and 4 do_all
        # patterns, where the other five produce 4 blockers and 3 patterns —
        # from dependence data that is byte-identical once the pointer-derived
        # memory-region ids are normalised.  The explorer is deterministic given
        # a fixed .discopop (8/8), so the outcome is varying with the region ids
        # themselves.  Reported rather than retried, so the instability stays
        # visible instead of being papered over.
        return Result("dependence review", "skip",
                      "0 blockers from this profile — upstream explorer instability "
                      "(see the comment here), not an agent fault; re-run to exercise "
                      "the review path")

    from ..llm import dep_review as dr
    from ..args import AgentArguments

    before = len(static.read_text().splitlines())
    # Stub the model's verdicts and the explorer re-run: this check is about the
    # plumbing between a verdict and the dependence file, not about either.
    real_review = dr.review_dependences
    real_run = dr.subprocess.run                      # type: ignore[attr-defined]
    setattr(dr, "review_dependences", lambda items, code, model, **kw: {
        i: (False, "stub") for i in range(1, len(items) + 1)})
    setattr(dr.subprocess, "run", lambda *a, **k: type(  # type: ignore[attr-defined]
        "R", (), {"returncode": 0, "stdout": "", "stderr": ""})())
    try:
        src = d / src_name
        old_text = src.read_text()
        lines = old_text.splitlines()
        # mark the loop body as rewritten, which is the scope the review covers
        new_text = "\n".join(l + ("  // touched" if 18 <= i + 1 <= 23 else "")
                             for i, l in enumerate(lines)) + "\n"
        src.write_text(new_text)
        out = d / "out"
        out.mkdir(exist_ok=True)
        args = AgentArguments(
            discopop_dir=str(d / ".discopop"), source_file=str(src), budget=1,
            model="haiku", api_key=None, provider="claude-agent-sdk", api_base=None,
            lambda_penalty=1.0, min_workload=0.0, output_dir=str(out), dry_run=False,
            edit_mode="direct", llm_pragmas=True, pragma_arbitration=True, fast_refresh=True, llm_deps=True,
            hotspots=False, min_impact=0.0, restructure_depth=0, require_speedup=False,
            judge_as_shipped=False, requeue_rejected=False, phase_b_reuse_d40=False,
            build_retries=2, apply_patches=True, min_measured_speedup=1.1,
            check_inputs=[], reprofil_args=[], verbose=False)
        note = dr._llm_dep_review(args, d / ".discopop", old_text, new_text, out, 1)
    finally:
        setattr(dr, "review_dependences", real_review)
        setattr(dr.subprocess, "run", real_run)       # type: ignore[attr-defined]

    after = len(static.read_text().splitlines())
    if after >= before:
        return Result("dependence review", "fail",
                      f"every blocker discharged but no dependence line removed "
                      f"({before} lines before and after) — {note}")
    return Result("dependence review", "pass",
                  f"{before - after} dependence line(s) removed — {note}")


def check_hotspot_remap(work: Path) -> Result:
    """Runtime measurements must move with the code, or be dropped.

    Hotspots are keyed by line number.  After a rewrite shifts lines they do not
    merely go stale — a region inherits whatever used to sit at its line number,
    and is then ranked confidently on another region's runtime.  That is worse
    than having no measurement at all, and nothing downstream can detect it.
    """
    from ..plan.impact import Hotspot, ImpactModel
    from ..profiling.fast_refresh import line_map

    m = ImpactModel(threads=8, total_runtime=1.0)
    m.by_line = {
        (1, 10): Hotspot(1, 10, "LOOP", "", "MAYBE", 0.01),
        (1, 20): Hotspot(1, 20, "LOOP", "", "YES", 0.90),
    }
    m.mark_covered(1, 20, 25)

    old = "\n".join(f"line{i}" for i in range(1, 31))
    new = "\n".join(["added"] * 5 + [f"line{i}" for i in range(1, 31)])
    dropped = m.remap_lines(1, line_map(old, new))

    hot = m.by_line.get((1, 25))
    if hot is None or abs(hot.avg_runtime - 0.90) > 1e-9:
        return Result("hotspot remap", "fail",
                      f"the hot measurement did not move to line 25: "
                      f"{sorted(m.by_line)}")
    if (1, 20) in m.by_line and m.by_line[(1, 20)].avg_runtime == 0.90:
        return Result("hotspot remap", "fail",
                      "the hot measurement is still pinned to its old line")
    if m.covered != [(1, 25, 30)]:
        return Result("hotspot remap", "fail",
                      f"covered spans did not move with it: {m.covered}")

    # a measurement whose line is deleted must be dropped, never re-pointed
    m2 = ImpactModel(threads=8, total_runtime=1.0)
    m2.by_line = {(1, 3): Hotspot(1, 3, "LOOP", "", "YES", 0.5)}
    gone = m2.remap_lines(1, line_map("a\nb\nGONE\nd\n", "a\nb\nd\n"))
    if gone != 1 or m2.by_line:
        return Result("hotspot remap", "fail",
                      f"a deleted line's measurement survived: {m2.by_line}")
    # Freshly re-measured runtimes are already in new coordinates: only the covered
    # spans move (the full re-profile path at depth >= 1).
    m3 = ImpactModel(threads=8, total_runtime=1.0)
    m3.by_line = {(1, 25): Hotspot(1, 25, "LOOP", "", "YES", 0.90)}
    m3.mark_covered(1, 20, 25)
    m3.remap_lines(1, line_map(old, new), measurements=False)
    if sorted(m3.by_line) != [(1, 25)] or m3.covered != [(1, 25, 30)]:
        return Result("hotspot remap", "fail",
                      f"covered-only remap moved the wrong thing: {sorted(m3.by_line)} {m3.covered}")

    # A reverted rewrite puts the source back; the measurements must go back too.
    m4 = ImpactModel(threads=8, total_runtime=1.0)
    m4.by_line = {(1, 3): Hotspot(1, 3, "LOOP", "", "YES", 0.5)}
    m4.mark_covered(1, 3, 4)
    before = m4.snapshot()
    m4.remap_lines(1, line_map("a\nb\nGONE\nd\n", "a\nb\nd\n"))
    m4.restore(before)
    if sorted(m4.by_line) != [(1, 3)] or m4.covered != [(1, 3, 4)]:
        return Result("hotspot remap", "fail",
                      f"a revert did not restore the measurements: {sorted(m4.by_line)} {m4.covered}")

    # The span a kept rewrite covers is what it CHANGED, without the diff's context.
    from ..pragmas import changed_span
    a_text = "\n".join(f"line{i}" for i in range(1, 21)) + "\n"
    b_text = a_text.replace("line10\n", "new10a\nnew10b\nnew10c\n").replace("line12\n", "")
    span = changed_span(make_diff(a_text, b_text, "f.c"))
    if span != (10, 13):
        return Result("hotspot remap", "fail", f"changed span read as {span}, want (10, 13)")
    # What a kept rewrite covers.  A pragma-free rewrite covers NOTHING: the loops it
    # exposed are what Phase B has to annotate, and a covered region is dropped from
    # every later queue (review F20).  An annotated one covers the loops that are
    # actually PARALLEL, not everything that was edited (review F21).
    from ..phases.phase_a import covered_spans_after
    fn_old = ("void f(int n) {\n  int i;\n  for (i = 0; i < n; i++)\n    a[i] = a[i] * 2;\n"
              "  for (i = 1; i < n; i++)\n    b[i] = b[i-1] + a[i];\n}\n")
    fn_new = fn_old.replace("  for (i = 0; i < n; i++)\n", "  #pragma omp parallel for\n  for (i = 0; i < n; i++)\n", 1)
    d_fn = make_diff(fn_old, fn_new, "f.c")
    if covered_spans_after(1, 7, fn_old, fn_new, d_fn, self_annotated=False):
        return Result("hotspot remap", "fail",
                      "a pragma-free rewrite marked its region covered — Phase B would then "
                      "never see the loops it exposed")
    got_spans = covered_spans_after(1, 7, fn_old, fn_new, d_fn, self_annotated=True)
    if got_spans != [(4, 5)]:
        return Result("hotspot remap", "fail",
                      f"an annotated rewrite of f() covers {got_spans}, want only its parallel loop [(4, 5)]")
    # The function keeps what is still sequential in it; the sibling loop stays visible.
    m5 = ImpactModel(threads=8, total_runtime=1.0)
    m5.by_line = {(1, 1): Hotspot(1, 1, "FUNCTION", "f", "YES", 0.90),
                  (1, 4): Hotspot(1, 4, "LOOP", "", "YES", 0.50),
                  (1, 6): Hotspot(1, 6, "LOOP", "", "YES", 0.40)}
    m5.mark_covered(1, 4, 5, m5.fraction(1, 4, 5))
    left = (m5.remaining_fraction(1, 1, 8), m5.remaining_fraction(1, 4, 5),
            m5.remaining_fraction(1, 5, 5), m5.remaining_fraction(1, 6, 7))
    want = (0.40, 0.0, 0.0, 0.40)
    if any(g is None or abs(g - w) > 1e-9 for g, w in zip(left, want)):
        return Result("hotspot remap", "fail",
                      f"remaining shares (function, parallel loop, its body, sibling loop) = {left}, want {want}")
    return Result("hotspot remap", "pass",
                  f"measurements and covered spans follow the code; "
                  f"{dropped} dropped when lines vanish; a revert restores them; "
                  f"a rewrite's span excludes diff context")


def check_mixed_scale_ranking(work: Path) -> Result:
    """A measured region must outrank an unmeasured one, whatever the proxy says.

    When only some regions have measurements the sort compares two incompatible
    scales — seconds against a log-workload proxy — and descending order then
    puts every unmeasured region ahead of every measured one. A region saving a
    real 0.3 ms lost to one the proxy merely scored 19.6.
    """
    from ..plan.impact import Hotspot, ImpactModel
    from ..plan.scoring import build_candidates

    # Exercised through the real sort by way of a tiny synthetic profile: the
    # planner needs Data.xml, so this checks the ordering rule directly on the
    # same key the planner uses.
    from ..types import CodeRegion, HotspotCandidate

    def cand(rid: str, lo: int, hi: int, impact_s: Optional[float],
             score: float) -> HotspotCandidate:
        r = CodeRegion(region_id=rid, region_type="loop", name="", file_id=1,
                       start_line=lo, end_line=hi, iteration_count=1, workload=1)
        return HotspotCandidate(region=r, source_file="x", pattern=None,
                                pattern_type=None, confidence=0.3,
                                workload_estimate=1.0, score=score, tier=2,
                                impact_seconds=impact_s,
                                runtime_fraction=0.9 if impact_s else None,
                                hotness="YES" if impact_s else None)

    measured = cand("measured", 10, 12, 0.0003, 0.0003)
    unmeasured = cand("unmeasured", 40, 44, None, 19.6)

    def rank(c: HotspotCandidate) -> Tuple[int, float, int]:
        un = 1 if c.impact_seconds is None else 0
        return (un, -c.score, -(c.region.end_line - c.region.start_line))

    order = [c.region.region_id for c in sorted([unmeasured, measured], key=rank)]
    if order[0] != "measured":
        return Result("mixed-scale ranking", "fail",
                      f"unmeasured region ranked first: {order}")
    # and with no measurements anywhere, the proxy order must be untouched
    a = cand("small", 1, 2, None, 1.0)
    b = cand("big", 3, 4, None, 20.0)
    plain = [c.region.region_id for c in sorted([a, b], key=lambda c: (0, -c.score, 0))]
    if plain[0] != "big":
        return Result("mixed-scale ranking", "fail",
                      f"proxy-only ordering changed: {plain}")
    return Result("mixed-scale ranking", "pass",
                  "measured beats unmeasured; proxy-only ordering unchanged")


# ---------------------------------------------------------------------------
# Correctness-gate calibration: comparison rules, noise floor, schedule matrix
# ---------------------------------------------------------------------------

# Real LULESH 2.0 output, serial build vs the stock OpenMP build at 48 threads,
# measured at -s 30 -i 200.  This pair is the reason the numeric comparison
# exists: it is LLNL's OWN reference parallelization, and a byte-identical gate
# reverts it.  The energy differs from the 16th digit and the symmetry residuals
# differ by more than 2x — the residuals being roundoff measured directly, which
# is why they must be judged against the output's scale, not their own.
_LULESH_SERIAL = """Run completed:
   Problem size        =  30
   Iteration count     =  200
   Final Origin Energy =  8.10592723224514280e+05
   Testing Plane 0 of Energy Array on rank 0:
        MaxAbsDiff   = 2.04636307898908854e-12
        TotalAbsDiff = 2.05779837614272765e-12
"""
_LULESH_OMP48 = """Run completed:
   Problem size        =  30
   Iteration count     =  200
   Final Origin Energy =  8.10592723224514397e+05
   Testing Plane 0 of Energy Array on rank 0:
        MaxAbsDiff   = 9.09494701772928238e-13
        TotalAbsDiff = 9.21013265653414237e-13
"""


def check_output_equivalence(work: Path) -> Result:
    """The comparison must accept reordered arithmetic and nothing else."""
    from ..gate.equivalence import compare_outputs
    floor = 1e-14
    ser, omp = _LULESH_SERIAL, _LULESH_OMP48
    cases: List[Tuple[str, bool, str, str, float]] = [
        # what it is,                        should pass, expected, got, floor
        ("LULESH serial vs its own OpenMP",  True,  ser, omp, floor),
        ("identical output",                 True,  ser, ser, floor),
        ("no floor -> byte-exact",           False, ser, omp, 0.0),
        ("iteration count changed",          False, ser,
         omp.replace("=  200", "=  199"), floor),
        ("a printed line disappears",        False, ser,
         "\n".join(l for l in omp.splitlines() if "TotalAbsDiff" not in l) + "\n", floor),
        ("a label changed",                  False, ser,
         omp.replace("MaxAbsDiff", "MaxAbsDif0"), floor),
        ("energy corrupted, 7th digit",      False, ser,
         omp.replace("8.10592723224514397e+05", "8.10592109224514397e+05"), floor),
        ("a value became nan",               False, ser,
         omp.replace("9.09494701772928238e-13", "nan"), floor),
        ("integer output, value changed",    False,
         "total 4950\ncount 100\n", "total 4951\ncount 100\n", 1e-6),
    ]
    bad = []
    for name, want, exp, got, fl in cases:
        m = compare_outputs(exp, got, fl)
        if m.equal != want:
            bad.append(f"{name}: expected {'accept' if want else 'reject'}, "
                       f"got {'accept' if m.equal else 'reject'} ({m.mode})")
    if bad:
        return Result("equivalence", "fail", "; ".join(bad))
    return Result("equivalence", "pass",
                  f"{len(cases)} comparison rules hold, LULESH's own OpenMP included")


def check_noise_floor(work: Path) -> Result:
    """A reducing program must measure a floor; an integer one must measure zero.

    The zero case is what keeps every existing benchmark case byte-exact, and
    the non-zero case is what stops the gate reverting correct parallel sums.
    """
    from ..gate.equivalence import numerical_noise_floor
    from ..gate.toolchain import _find_clangpp
    if _find_clangpp() is None:
        return Result("noise-floor", "skip", "no supported clang++ found")

    d = work / "floor"
    d.mkdir(parents=True, exist_ok=True)
    fp = d / "reduce.cpp"
    fp.write_text(
        "#include <cstdio>\n#include <cmath>\n"
        "int main(){const int N=2000000;double*a=new double[N];\n"
        "for(int i=0;i<N;i++)a[i]=std::sin(i*0.0001)*1e3+1.0/(i+1);\n"
        "double s=0.0;for(int i=0;i<N;i++)s+=a[i];\n"
        "printf(\"count %d\\nsum %.17e\\n\",N,s);delete[] a;return 0;}\n"
    )
    ints = d / "ints.cpp"
    ints.write_text(
        "#include <cstdio>\n"
        "int main(){long t=0;for(int i=0;i<100;i++)t+=i;\n"
        "printf(\"total %ld\\n\",t);return 0;}\n"
    )
    f_float = numerical_noise_floor(str(fp))
    f_int = numerical_noise_floor(str(ints))
    if f_int.value != 0.0:
        return Result("noise-floor", "fail",
                      f"integer-only program measured a non-zero floor {f_int.value:.2e} "
                      f"— existing cases would stop being byte-exact")
    if f_float.value <= 0.0:
        return Result("noise-floor", "fail",
                      "a two-million-element float reduction measured a floor of 0; "
                      "the reassociating build variant is not taking effect, so correct "
                      "parallel sums would be reverted")
    return Result("noise-floor", "pass",
                  f"reduction {f_float.value:.1e}, integer program 0 (stays strict)")


def check_schedule_stress(work: Path) -> Result:
    """A race must fail on repeatability; a correct reduction must survive."""
    from ..gate.equivalence import numerical_noise_floor
    from ..gate.patching import _compile_variant
    from ..gate.schedules import stress_schedules
    from ..gate.toolchain import _find_clangpp
    clangpp = _find_clangpp()
    if clangpp is None:
        return Result("schedule-stress", "skip", "no supported clang++ found")

    d = work / "stress"
    d.mkdir(parents=True, exist_ok=True)
    racy = d / "racy.cpp"
    # An unsynchronised histogram, not `s += i`.  With a single accumulator at
    # -O2 clang keeps the sum in a per-thread register and stores roughly once
    # per chunk, so there are only a handful of racing writes and the lost
    # update frequently does not happen — the check failed about half the time
    # for that reason alone.  Many threads hammering eight shared counters
    # cannot be register-promoted and loses updates on essentially every run.
    racy.write_text(
        "#include <cstdio>\n"
        "int main(){const int N=4000000;long long h[8]={0,0,0,0,0,0,0,0};\n"
        "#pragma omp parallel for\n"
        "for(int i=0;i<N;i++)h[i&7]+=1;\n"
        "long long t=0;for(int k=0;k<8;k++)t+=h[k];\n"
        "printf(\"count %d\\ntotal %lld\\n\",N,t);return 0;}\n"
    )
    good = d / "good.cpp"
    good.write_text(
        "#include <cstdio>\n#include <cmath>\n"
        "int main(){const int N=2000000;double*a=new double[N];\n"
        "for(int i=0;i<N;i++)a[i]=std::sin(i*0.0001)*1e3+1.0/(i+1);\n"
        "double s=0.0;\n"
        "#pragma omp parallel for reduction(+:s)\n"
        "for(int i=0;i<N;i++)s+=a[i];\n"
        "printf(\"count %d\\nsum %.17e\\n\",N,s);delete[] a;return 0;}\n"
    )
    out = []
    for src, expect_ok in ((racy, False), (good, True)):
        ok_b, diag, binary = _compile_variant(src, clangpp, d, f"b_{src.stem}", openmp=True)
        if not ok_b or binary is None:
            return Result("schedule-stress", "skip",
                          f"no working -fopenmp build ({diag.splitlines()[0][:60] if diag else '?'})")
        floor = numerical_noise_floor(str(src)).value if expect_ok else 0.0
        st = stress_schedules(binary, d, None, floor=floor)
        if st.ok != expect_ok:
            return Result("schedule-stress", "fail",
                          f"{src.name}: expected {'pass' if expect_ok else 'race'}, "
                          f"got verdict={st.verdict} ({st.diagnostic[:110]})")
        if not expect_ok and not st.hard:
            return Result("schedule-stress", "fail",
                          f"{src.name}: a race must be a hard failure, not overridable")
        out.append(f"{src.stem}={st.verdict}")
    return Result("schedule-stress", "pass",
                  f"{', '.join(out)}; race caught by repeatability, not by a diff")


def check_anchor_correctness(work: Path) -> Result:
    """The schedule matrix must be checked against the REFERENCE, not only itself.

    Its seven runs used to be compared only to each other, so a parallelization
    that is perfectly self-consistent and simply computes the wrong answer
    passed this stage without comment and relied on the later correctness run.
    A deterministic-but-wrong pragma must now fail here, and a correct one must
    still pass.
    """
    from ..gate.timing import capture_reference
    from ..gate.toolchain import _find_clangpp
    from ..gate.validate import validate
    from ..llm import make_diff
    if _find_clangpp() is None:
        return Result("anchor-vs-ref", "skip", "no supported clang++ found")

    orig = (
        "#include <cstdio>\n"
        "int main(){\n"
        "    long s = 0;\n"
        "    for (int i = 0; i < 200000; i++) { s += i; }\n"
        '    printf("%ld\\n", s);\n'
        "    return 0;\n"
        "}\n"
    )
    par = "    #pragma omp parallel for reduction(+:s)\n    for (int i = 0; i < 200000;"
    right = orig.replace("    for (int i = 0; i < 200000;", par)
    # deterministic under every thread count and schedule, and short by one element
    wrong = right.replace("i < 200000", "i < 199999")

    d = work / "anchor"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "m.cpp"
    src.write_text(orig)
    ref, _t, refs = capture_reference(str(src))
    if ref is None:
        return Result("anchor-vs-ref", "skip", "could not capture a reference")

    notes = []
    for label, text, want_pass in (("wrong", wrong, False), ("correct", right, True)):
        r = validate(make_diff(orig, text, str(src)), str(src),
                     reference_output=ref, reference_outputs=refs,
                     mode="safety", stress=True, stress_threads=(1, 2, 4))
        if r.passed != want_pass:
            return Result("anchor-vs-ref", "fail",
                          f"{label} parallelization: expected passed={want_pass}, "
                          f"got passed={r.passed} at stage {r.stage!r}")
        if label == "wrong":
            if "at a fixed thread count" not in (r.diagnostic or ""):
                return Result("anchor-vs-ref", "fail",
                              "the wrong pragma failed, but not at the schedule "
                              f"anchor — stage {r.stage!r}. The anchor-vs-reference "
                              "comparison did not fire.")
            notes.append("deterministic-but-wrong caught at the anchor")
        else:
            notes.append("correct reduction still passes")
    return Result("anchor-vs-ref", "pass", "; ".join(notes))


def check_dependence_evidence(work: Path) -> Result:
    """The profile must contradict a pragma on a real recurrence, and abstain otherwise.

    Four verdicts, and the three non-failing ones matter as much as the failing
    one: a stage that answered "looks fine" where it knows nothing would be
    worse than no stage at all.  The recurrence here is deliberately an ARRAY
    one (`a[i] = a[i-1] + 2`) rather than an accumulator: `run += a[i]` is a
    reduction, which the detector is right not to record as a blocker, and
    testing with it would assert the opposite of correct behaviour.
    """
    from ..gate.dependences import dependence_evidence

    if dependence_evidence(None, None, None, None).verdict != "unavailable":
        return Result("dep-evidence", "fail", "no profile did not give 'unavailable'")
    if dependence_evidence(str(work / "nope"), 1, 1, 10).verdict != "unavailable":
        return Result("dep-evidence", "fail", "missing .discopop did not give 'unavailable'")

    d = work / "depev"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "recurrence.cpp"
    src.write_text(
        "#include <cstdio>\n"
        "int main() {\n"
        "  const int N = 20000;\n"
        "  static long a[20000];\n"
        "  for (int i = 0; i < N; i++) {\n"
        "    a[i] = i;\n"
        "  }\n"
        "  for (int i = 1; i < N; i++) {\n"
        "    a[i] = a[i - 1] + 2;\n"
        "  }\n"
        "  printf(\"last %ld\\n\", a[N - 1]);\n"
        "  return 0;\n"
        "}\n"
    )
    ok, err = _profile(d, src.name, hotspots=False)
    if not ok:
        return Result("dep-evidence", "skip", f"could not profile ({err[:70]})")
    dp = str(d / ".discopop")

    rec = dependence_evidence(dp, 1, 8, 9)      # a[i] = a[i-1] + 2
    clean = dependence_evidence(dp, 1, 5, 6)    # a[i] = i
    gap = dependence_evidence(dp, 1, 900, 910)  # nothing there

    if rec.verdict != "contradicted":
        return Result("dep-evidence", "fail",
                      f"a true array recurrence gave '{rec.verdict}', expected "
                      f"'contradicted' ({rec.diagnostic[:90]})")
    if clean.verdict != "no-blocker":
        return Result("dep-evidence", "fail",
                      f"a clean Do-All gave '{clean.verdict}', expected 'no-blocker'")
    if gap.verdict != "no-data":
        return Result("dep-evidence", "fail",
                      f"unprofiled lines gave '{gap.verdict}', expected 'no-data'")
    if "not proof" not in clean.diagnostic.lower():
        return Result("dep-evidence", "fail",
                      "'no-blocker' must not read as a clean bill of health")
    return Result("dep-evidence", "pass",
                  "recurrence=contradicted, clean loop=no-blocker, "
                  "unprofiled=no-data, no profile=unavailable")


def check_dep_line_resolution(work: Path) -> Result:
    """A dependence must be attributed to the line it is actually on.

    The endpoints in dynamic_dependencies.txt are instruction ids, and the
    number after an `@` is callpath STATE, not a line.  Reading it as a line
    put a region's dependences almost anywhere: the `fileID:lineID` form
    resolved to line 0 and was dropped from every region, and the rest landed
    wherever the state number happened to point.  This pins the fix by asking
    for a loop whose carried dependence is known by construction.
    """
    from ..evidence.deps import _load_dependencies

    d = work / "depev"
    dp = d / ".discopop" / "profiler"
    if not (dp / "dynamic_dependencies.txt").exists():
        return Result("dep-lines", "skip", "no profile available (dep-evidence skipped)")

    raw, war, waw = _load_dependencies(dp, 8, 9)     # a[i] = a[i-1] + 2
    if not raw:
        return Result("dep-lines", "fail",
                      "the recurrence loop reported no RAW dependence at all — "
                      "endpoints are not being resolved to source lines")
    carried = [dep for dep in raw if dep.from_line == 9 and dep.to_line == 9]
    if not carried:
        placed = sorted({(dep.from_line, dep.to_line) for dep in raw})
        return Result("dep-lines", "fail",
                      f"no loop-carried RAW on line 9; dependences landed at {placed[:6]}")
    # And nothing may be attributed to a line the file does not have.
    n_lines = len((d / "recurrence.cpp").read_text().splitlines())
    stray = [dep for dep in raw + war + waw
             if dep.from_line > n_lines or dep.to_line > n_lines]
    if stray:
        return Result("dep-lines", "fail",
                      f"{len(stray)} dependence(s) attributed past the end of a "
                      f"{n_lines}-line file, e.g. {stray[0]}")
    return Result("dep-lines", "pass",
                  f"{len(carried)} loop-carried RAW found on line 9; "
                  f"{len(raw + war + waw)} deps all within {n_lines} lines")


def check_omp_include(work: Path) -> Result:
    """A candidate that includes <omp.h> must build wherever OpenMP builds.

    On macOS the gate linked Homebrew's libomp (-L) but never added its headers
    (-I), and that LLVM ships no omp.h of its own.  Every candidate calling an
    OpenMP runtime function (omp_get_thread_num, omp_get_wtime, ...) was rejected
    at the OpenMP compile on the Mac only — reported as if the model had written
    invalid code.
    """
    from ..gate.patching import _compile_variant
    from ..gate.toolchain import _find_clangpp

    name = "omp include"
    clangpp = _find_clangpp()
    if clangpp is None:
        return Result(name, "skip", "no supported clang")
    d = work / "omp_include"
    d.mkdir(parents=True, exist_ok=True)
    body = ("#include <omp.h>\n#include <stdio.h>\n"
            "int main(void) {\n    int n = 0;\n    #pragma omp parallel reduction(+:n)\n"
            "    n += 1;\n    printf(\"%d %d\\n\", n > 0, omp_get_max_threads() > 0);\n"
            "    return 0;\n}\n")
    failed: List[str] = []
    for ext in (".c", ".cpp"):
        src = d / f"probe{ext}"
        src.write_text(body)
        ok, diag, binary = _compile_variant(src, clangpp, d, f"probe_{ext[1:]}", openmp=True)
        if not ok or binary is None:
            first = diag.strip().splitlines()[0][:100] if diag.strip() else "build failed"
            failed.append(f"{ext}: {first}")
            continue
        r = subprocess.run([str(binary)], capture_output=True, text=True, timeout=60)
        if r.returncode != 0 or r.stdout.strip() != "1 1":
            failed.append(f"{ext}: exit {r.returncode}, output {r.stdout.strip()!r}")
    if failed:
        return Result(name, "fail", "; ".join(failed))
    return Result(name, "pass", "C and C++ programs including <omp.h> build with -fopenmp and run")


def check_omp_runtime(work: Path) -> Result:
    """A candidate that CALLS the OpenMP runtime is judged by the gate, not refused at compile.

    The gate's plain compile linked without OpenMP, so `omp_get_thread_num()` failed there
    whatever the program computed — `s341` rep 5 of E1-bare's model alone, harness-verified
    FASTER, came back from the gate as a `compile` failure (Fix 92). The same candidate must
    now reach the race and output stages and pass them; a racy one must still fail there."""
    from ..gate import validate
    from ..gate.timing import capture_reference
    from ..gate.toolchain import _find_clangpp
    from ..llm import make_diff

    name = "omp runtime"
    if _find_clangpp() is None:
        return Result(name, "skip", "no supported clang")
    d = work / "omp_runtime"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "sum.c"
    orig = ("#include <stdio.h>\nint main(void) {\n    static double a[4000];\n"
            "    for (int i = 0; i < 4000; i++) a[i] = i;\n    double s = 0;\n"
            "    for (int i = 0; i < 4000; i++) s += a[i];\n"
            "    printf(\"%.1f\\n\", s);\n    return 0;\n}\n")
    src.write_text(orig)
    ref_out, _t, ref_pairs = capture_reference(str(src))
    if ref_out is None:
        return Result(name, "fail", "the original did not build")
    per_thread = ("#include <stdio.h>\n#include <omp.h>\nint main(void) {\n    static double a[4000];\n"
                  "    for (int i = 0; i < 4000; i++) a[i] = i;\n    double part[512] = {0};\n"
                  "    int T = omp_get_max_threads();\n    #pragma omp parallel\n    {\n"
                  "        int t = omp_get_thread_num();\n        double loc = 0;\n"
                  "        #pragma omp for\n        for (int i = 0; i < 4000; i++) loc += a[i];\n"
                  "        part%s += loc;\n    }\n    double s = 0;\n"
                  "    for (int t = 0; t < T; t++) s += part[t];\n"
                  "    printf(\"%%.1f\\n\", s);\n    return 0;\n}\n")
    verdicts = {}
    for label, text in (("per-thread partial sums", per_thread % "[t]"),
                        ("every thread adds into part[0]", per_thread % "[0]")):
        res = validate(make_diff(orig, text, str(src)), str(src), reference_output=ref_out,
                       reference_outputs=ref_pairs, mode="safety")
        verdicts[label] = (res.passed, res.stage)
    good, racy = verdicts["per-thread partial sums"], verdicts["every thread adds into part[0]"]
    if not good[0]:
        return Result(name, "fail", f"a correct program calling the runtime failed at '{good[1]}'")
    if racy[0] or racy[1] in ("compile", "apply"):
        return Result(name, "fail", f"a racy program calling the runtime was not caught by a race or "
                                    f"output stage (verdict {racy})")
    return Result(name, "pass", f"a correct runtime-calling program passes the gate; a racy one fails at "
                                f"'{racy[1]}'")


_TIMING_LOOP = "    for (int i = 0; i < N; i++) a[i] = i;\n"
_TIMING_PROBE = (
    "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
    "#ifdef DP_TIMING_BREAK\n#error \"timing flags reached this build\"\n#endif\n"
    "#define N 1000\nstatic int a[N];\nint main(void) {\n"
    + _TIMING_LOOP
    + "    long s = 0;\n    for (int i = 0; i < N; i++) s += a[i];\n"
    "    printf(\"sum %ld\\n\", s);\n"
    "#ifdef DP_TIMING_BIG\n    int parallel = 0;\n#  ifdef _OPENMP\n"
    "    const char *t = getenv(\"OMP_NUM_THREADS\");\n"
    "    parallel = !(t && strcmp(t, \"1\") == 0);\n#  endif\n"
    "    fprintf(stderr, \"DP_TIMED_REGION_SECONDS %s\\n\", parallel ? \"0.25\" : \"0.5\");\n"
    "#else\n    fprintf(stderr, \"DP_TIMED_REGION_SECONDS 0.001\\n\");\n#endif\n"
    "    return 0;\n}\n"
)


def check_timing_size(work: Path) -> Result:
    """--timing-cflags must reach every build the speed check times, and no other.

    The option lets a program be profiled and checked at a small size and timed
    at one where speed is measurable.  Its failure would be silent: a timed build
    that drops the flag measures the small size again, so the speed check goes
    back to judging noise while the run says it timed the large one; and a
    correctness build that picked the flag up would compare two sizes' outputs.

    The probe REPORTS its timed region instead of computing one, so the check is
    deterministic: with DP_TIMING_BIG it reports 0.5 s when built without OpenMP
    or run with OMP_NUM_THREADS=1 (what the speed measurement sets for its
    sequential side), 0.25 s otherwise (a 2.0x speedup); without the flag 0.001 s
    either way.  It reads OMP_NUM_THREADS instead of calling omp_get_max_threads,
    so it needs no omp.h — which a macOS LLVM may not have on its include path.
    DP_TIMING_BREAK makes the build fail, which proves a function compiled with
    the flags.
    """
    from ..gate.timing import capture_reference, measure_marginal, noise_floor, time_source
    from ..gate.toolchain import _find_clangpp
    from ..gate.validate import validate
    from ..llm import make_diff

    name = "timing size"
    if _find_clangpp() is None:
        return Result(name, "skip", "no supported clang")
    if (os.cpu_count() or 1) < 2:
        return Result(name, "skip", "needs at least 2 cores")
    d = work / "timing"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "probe.c"
    src.write_text(_TIMING_PROBE)
    big, broken = ["-DDP_TIMING_BIG"], ["-DDP_TIMING_BREAK"]
    problems: List[str] = []

    out, ref_small, _ = capture_reference(str(src))
    out_big, ref_big, _ = capture_reference(str(src), timing_flags=big)
    if out is None or out != out_big or ref_small != 0.001 or ref_big != 0.5:
        problems.append(f"reference: times {ref_small}/{ref_big} (expected 0.001/0.5), "
                        f"output {'unchanged' if out == out_big else 'CHANGED'}")
    if capture_reference(str(src), timing_flags=broken)[0] is not None:
        problems.append("reference: a failing timing build was not fatal")

    text = src.read_text()
    ok_t, t_big, _o, tdiag = time_source(text, str(src), d, "t", extra_flags=big)
    if not ok_t or t_big not in (0.25, 0.5):
        problems.append(f"time_source: {t_big} with the flag, expected 0.25 ({tdiag[:60]})")
    if noise_floor(text, str(src), pairs=1, trials=1, extra_flags=broken)[0]:
        problems.append("noise_floor: built without the timing flags")
    if measure_marginal(text, text, str(src), pairs=1, extra_flags=broken)[0]:
        problems.append("measure_marginal: built without the timing flags")

    diff = make_diff(text, text.replace(_TIMING_LOOP, "#pragma omp parallel for\n" + _TIMING_LOOP),
                     str(src))
    timed = validate(diff, str(src), reference_output=out, require_speedup=True, min_speedup=1.1,
                     skip_race_check=True, stress=False, reference_time=ref_big, timing_flags=big)
    untimed = validate(diff, str(src), reference_output=out, require_speedup=True, min_speedup=1.1,
                       skip_race_check=True, stress=False, reference_time=ref_small)
    safety = validate(diff, str(src), reference_output=out, skip_race_check=True, stress=False,
                      timing_flags=broken)
    if not timed.passed:
        problems.append(f"gate with the flag failed at '{timed.stage}': {timed.diagnostic[:80]}")
    if untimed.passed or untimed.stage != "performance":
        problems.append(f"gate without the flag: expected a performance rejection, got '{untimed.stage}'")
    if not safety.passed:
        problems.append(f"correctness stages picked up the timing flags: failed at '{safety.stage}'")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass",
                  f"reference 0.001 → 0.5 s, timed builds and noise/marginal builds take the flag; "
                  f"gate {timed.measured_speedup:.1f}× with it, rejected at 'performance' without; "
                  f"correctness builds untouched")


def check_exclude_cxx(work: Path) -> Result:
    """--exclude-functions must work on C++, whose names DiscoPoP writes mangled.

    Data.xml names a C++ function `_ZL6helperv` (file-local), `_Z4workiPd` or
    `_ZN2ns6nestedEv`, while the caller writes `helper`, `work`, `nested`. The
    comparison used the raw name, so on every C++ program the exclusion list
    matched nothing and the agent could spend model calls on a benchmark's
    setup, output and timing code.
    """
    name = "exclude c++"
    d = work / "exclude_cxx"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "probe.cpp"
    src.write_text(
        "static int helper(int* a, int n) {\n  int s = 0;\n"
        "  for (int i = 0; i < n; i++) s += a[i];\n  return s;\n}\n"
        "namespace ns {\nint nested(int* a, int n) {\n  int s = 0;\n"
        "  for (int i = 0; i < n; i++) s ^= a[i];\n  return s;\n}\n}\n"
        "int kept(int* a, int n) {\n  int s = 0;\n"
        "  for (int i = 0; i < n; i++) s += 2 * a[i];\n  return s;\n}\n"
        "int main() {\n  int a[64];\n  for (int i = 0; i < 64; i++) a[i] = i;\n"
        "  return (helper(a, 64) + ns::nested(a, 64) + kept(a, 64)) > 0 ? 0 : 1;\n}\n")
    shutil.rmtree(d / ".discopop", ignore_errors=True)
    ok, err = _run([_venv_bin("discopop_cxx"), src.name, "-o", "a.out"], d)
    if not ok:
        return Result(name, "fail", f"discopop_cxx: {err[-160:]}")

    def spans(excl: Tuple[str, ...]) -> List[Tuple[str, int]]:
        cands = build_candidates(d / ".discopop", str(src), 1.0, min_workload=0,
                                 exclude_functions=excl)
        return sorted({(c.region.region_type, c.region.start_line) for c in cands})

    # The function regions themselves: an excluded function takes its own span and
    # everything inside it out of the queue. (Its loops need a profiled run for
    # iteration counts before they become candidates at all.)
    lines = src.read_text().splitlines()
    helper = next(i for i, l in enumerate(lines, 1) if "static int helper" in l)
    nested = next(i for i, l in enumerate(lines, 1) if "int nested" in l)
    kept = next(i for i, l in enumerate(lines, 1) if "int kept" in l)

    def has_fn(ss: List[Tuple[str, int]], line: int) -> bool:
        return ("function", line) in ss

    before = spans(())
    after = spans(("helper", "nested"))
    if not (has_fn(before, helper) and has_fn(before, nested) and has_fn(before, kept)):
        return Result(name, "fail", f"DiscoPoP did not report the three functions: {before}")
    problems = []
    if has_fn(after, helper):
        problems.append("the file-local `helper` (_ZL...) was not excluded")
    if has_fn(after, nested):
        problems.append("the namespaced `ns::nested` (_ZN...E) was not excluded")
    if not has_fn(after, kept):
        problems.append("`kept` was excluded although it is not on the list")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", f"{len(before)} -> {len(after)} candidates; `helper` (file-local) "
                                f"and `ns::nested` excluded by plain name, `kept` kept")


def check_new_region_ranking(work: Path) -> Result:
    """A loop a REWRITE created must still be rankable when Phase B gets to it.  (Fix 86)

    The two halves of the bug this pins:

      1. THE HAZARD.  With `--min-runtime-share` set, `build_candidates` drops a
         region the hotspot model has no measurement for instead of falling back to
         the workload proxy — sound for a region that existed when the runtimes were
         taken and was found cold, wrong for one that did not exist yet.
      2. THE CONSEQUENCE.  Runtimes were re-measured only when a DEEPER restructuring
         level was coming, so at the default `--restructure-depth 0` they never were.
         Every loop a rewrite exposed therefore reached Phase B unmeasured and was
         dropped, Phase B kept nothing, and Settle discarded the rewrite as an orphan
         — the whole restructuring path reporting `no-change`.  Measured on
         `tsvc/s211`: the model distributed the loop correctly, DiscoPoP reported
         `do_all` on BOTH halves, and the parallel one was never offered.

    So the re-measurement may not depend on the depth, and that is asserted here.
    """
    name = "new-region ranking"
    import inspect
    from ..phases.phase_a import should_remeasure_runtimes

    depends_on = [p for p in inspect.signature(should_remeasure_runtimes).parameters
                  if "depth" in p or "deeper" in p]
    if depends_on:
        return Result(name, "fail",
                      f"re-measuring runtimes still depends on {depends_on} — at "
                      f"--restructure-depth 0 the regions a rewrite created stay unmeasured")
    if not should_remeasure_runtimes(True, True, True):
        return Result(name, "fail", "runtimes are not re-measured after a kept rewrite")
    if should_remeasure_runtimes(True, False, True):
        return Result(name, "fail", "--no-hotspots must not trigger a runtime measurement")

    dp = work / ".discopop"
    src = str(work / "priority_mix.cpp")
    if not (dp / "hotspot_detection" / "Hotspots.json").exists():
        return Result(name, "skip", "needs the impact-ranking profile (invariant checked)")
    model = load_hotspots(dp, threads=8)
    full = build_candidates(dp, src, 1.0, 0.0, impact=model, min_runtime_share=0.01)
    if not full:
        return Result(name, "skip", "no candidate survives a 1 % share floor")

    # The state a rewrite leaves behind: the model was measured on the OLD program, so
    # NOTHING inside the region the rewrite created is in it.  `ImpactModel.lookup`
    # falls back to any measured line within the span, so dropping the start line
    # alone would still find one and would not reproduce the case.
    victim = min(full, key=lambda c: c.region.end_line - c.region.start_line)
    stale = load_hotspots(dp, threads=8)
    stale.by_line = {(f, l): h for (f, l), h in stale.by_line.items()
                     if not (f == victim.region.file_id
                             and victim.region.start_line <= l <= victim.region.end_line)}
    after = {c.region.region_id for c in
             build_candidates(dp, src, 1.0, 0.0, impact=stale, min_runtime_share=0.01)}
    if victim.region.region_id in after:
        return Result(name, "skip",
                      "this profile does not reproduce the hazard (invariant checked)")
    return Result(name, "pass",
                  f"an unmeasured region is dropped at a 1 % share floor "
                  f"({victim.region.region_id}), so runtimes are re-measured at every depth")


def check_hotspot_remeasure(work: Path) -> Result:
    """A forced re-measurement must describe the program AS IT NOW IS.  (Fix 87)

    DiscoPoP's hotspot detection accumulates by design: every instrumented build
    APPENDS its region ids to `hotspot_detection/private/cs_id.txt`, every run adds a
    `hotspot_result_<n>.txt`, and the analyzer averages over the runs.  Right for
    several inputs of one program; after a rewrite it is a different program.  The
    agent used to delete only `Hotspots.json` before re-measuring, so the analyzer
    reported the OLD region table: old line numbers, times halved by averaging with a
    run that never executed those ids, and nothing for a region the rewrite created —
    while the caller, believing the numbers were in the new file's coordinates,
    skipped the line remap.  Measured on `tsvc/s211`: `main` stayed at line 147 (149
    after the rewrite) and the loop the rewrite created at line 140 had no entry, so
    Fix 86 alone changed nothing.

    The check shifts every line of a measured program down by three and re-measures:
    every measured line must move with it, and none may stay behind.
    """
    name = "hotspot re-measure"
    from types import SimpleNamespace
    from ..profiling.runner import _measure_hotspots

    sub = work / "hs_remeasure"
    sub.mkdir(parents=True, exist_ok=True)
    src_name = "priority_mix.cpp"
    shutil.copy(_CASES / src_name, sub / src_name)
    dp = sub / ".discopop"
    ok, err = _profile(sub, src_name, hotspots=False)
    if not ok:
        return Result(name, "skip", err)
    args: Any = SimpleNamespace(source_file=str(sub / src_name), reprofil_args=None)
    ok, note = _measure_hotspots(args, dp)
    before = load_hotspots(dp, threads=8)
    if not ok or not before.available:
        return Result(name, "skip", f"no hotspot measurements produced ({note[:80]})")

    shift = 3
    (sub / src_name).write_text("// shifted\n" * shift + (sub / src_name).read_text())
    ok, note = _measure_hotspots(args, dp, force=True)
    after = load_hotspots(dp, threads=8)
    if not ok or not after.available:
        return Result(name, "fail", f"the forced re-measurement produced nothing ({note[:80]})")

    old_lines = sorted(l for _f, l in before.by_line)
    new_lines = sorted(l for _f, l in after.by_line)
    stale = [l for l in new_lines if l in old_lines and l - shift not in old_lines]
    moved = [l for l in old_lines if l + shift in new_lines]
    if len(moved) < len(old_lines) or stale:
        return Result(name, "fail",
                      f"the re-measurement still describes the old program: measured lines "
                      f"{old_lines} -> {new_lines} after a {shift}-line shift")
    # Averaged with a run that never executed the old ids, every time came out halved.
    ratio = after.total_runtime / before.total_runtime if before.total_runtime else 0.0
    if ratio < 0.7:
        return Result(name, "fail",
                      f"total runtime fell to {ratio:.2f}x on an unchanged program — the "
                      f"analyzer is still averaging the old run in")
    return Result(name, "pass",
                  f"{len(old_lines)} measured lines all moved by {shift}, none left behind; "
                  f"total runtime {ratio:.2f}x of the first measurement")


def check_explorer_stall(work: Path) -> Result:
    """A stalled explorer attempt is killed — whole process group — and the draw repeated.

    The explorer stalls at random on an unchanged profile (upstream report L5).  The agent's
    call had no time limit, so a stall after a KEPT rewrite hung the trial until the harness
    killed the agent at its 90-minute limit, and it could only hit trials whose rewrite had
    been accepted.  Tested with a stand-in explorer that hangs on its first attempt — with a
    child process of its own, as the real one has the patch generator — and succeeds on its
    second.
    """
    name = "explorer stall"
    import os
    import stat
    import time
    from ..profiling import tools

    sub = work / "explorer_stall"
    (sub / ".discopop").mkdir(parents=True, exist_ok=True)
    marker, childpid = sub / "second_attempt", sub / "child.pid"
    fake = sub / "fake_explorer.sh"
    fake.write_text(f"""#!/bin/sh
if [ -f "{marker}" ]; then mkdir -p explorer; echo '{{}}' > explorer/patterns.json; exit 0; fi
touch "{marker}"
sleep 300 &
echo $! > "{childpid}"
wait
""")
    fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
    saved_cmd, saved_limit = tools._explorer_cmd, tools.EXPLORER_STALL_S
    tools._explorer_cmd = lambda: str(fake)          # type: ignore[assignment]
    tools.set_explorer_timeout(2.0)
    try:
        t0 = time.time()
        r = tools.run_explorer(sub / ".discopop")
        took = time.time() - t0
    finally:
        tools._explorer_cmd = saved_cmd              # type: ignore[assignment]
        tools.set_explorer_timeout(saved_limit)
    if r.returncode != 0:
        return Result(name, "fail", f"the repeated draw did not succeed (rc={r.returncode})")
    if took > 30:
        return Result(name, "fail", f"took {took:.0f} s — the stalled attempt was not cut at its limit")
    time.sleep(0.3)
    try:
        os.kill(int(childpid.read_text().strip()), 0)
        return Result(name, "fail", "the stalled explorer's CHILD process survived the kill")
    except (ProcessLookupError, ValueError, FileNotFoundError):
        pass
    return Result(name, "pass",
                  f"stalled attempt killed with its child after 2 s, the next draw succeeded ({took:.1f} s)")


_LOOP_COUNT_SRC = """#include <stdio.h>
#define N 1000
#define R 7
static double a[N], b[N];
int main(void) {
  for (int i = 0; i < N; i++) { a[i] = i; b[i] = 2 * i; }
  for (int r = 0; r < R; r++) {
    for (int i = 1; i < N - 1; i++) { b[i] = b[i + 1] - a[i]; }
    for (int i = 1; i < N - 1; i++) { a[i] = b[i - 1] + a[i]; }
  }
  double s = 0; for (int i = 0; i < N; i++) s += a[i] + b[i];
  printf("%f\\n", s); return 0;
}
"""


def check_loop_counts(work: Path) -> Result:
    """The iteration counts the agent uses are the OBSERVED ones.  (Fix 88)

    DiscoPoP's loop_counter_output.txt pairs its counts with the wrong loops (upstream B7;
    82 % of 337 loop counts wrong over 41 profiles).  The agent read that file for the
    workload proxy and for the "N iterations" it states in the prompt header, so a
    48-iteration outer loop was presented to the model as running 1,536,000 times.  The
    counts are now read from the `BGN loop` markers.  Ground truth here is by construction:
    an outer loop of 7 around two sibling loops of 998.
    """
    name = "loop counts"
    from ..plan.regions import _load_loop_counts

    sub = work / "loop_counts"
    sub.mkdir(parents=True, exist_ok=True)
    (sub / "lc.c").write_text(_LOOP_COUNT_SRC)
    ok, err = _profile(sub, "lc.c", hotspots=False, c_as_c=True)
    if not ok:
        return Result(name, "skip", err)
    counts = _load_loop_counts(sub / ".discopop" / "profiler")
    lines = (sub / "lc.c").read_text().splitlines()
    at = {i + 1: l for i, l in enumerate(lines) if l.lstrip().startswith("for (")}
    outer = next(n for n, l in at.items() if "r < R" in l)
    siblings = [n for n, l in at.items() if "i < N - 1" in l]
    got = {n: counts.get(f"1:{n}") for n in [outer] + siblings}
    want = {outer: 7, siblings[0]: 7 * 998, siblings[1]: 7 * 998}
    if got != want:
        return Result(name, "fail", f"iteration counts {got}, expected {want}")
    raw = {}
    for l in (sub / ".discopop" / "profiler" / "loop_counter_output.txt").read_text().splitlines():
        parts = l.split()
        if len(parts) >= 3:
            raw[int(parts[1])] = int(parts[2])
    upstream = "still wrong upstream" if any(raw.get(n) != w for n, w in want.items()) else "upstream file agrees here"
    return Result(name, "pass",
                  f"outer loop 7, both sibling loops 6,986 — from the observed markers "
                  f"(loop_counter_output.txt: {upstream}: { {n: raw.get(n) for n in want} })")


def check_prompt_ablation(work: Path) -> Result:
    """E2's two instruments change EXACTLY what they name, in every edit mode.  (D16)

    `--prompt-omit` removes one part of the prompt so its contribution can be measured; an
    omission that took a second part with it — or left the part in one edit mode — would make
    the ablation measure something else.  `--evidence-file` shows another tool's remarks where
    DiscoPoP's digest goes; under `--evidence none` the request must then carry those remarks
    and NOTHING DiscoPoP measured.
    """
    import dataclasses
    from ..llm.prompts import PROMPT_PARTS, _system_prompt
    from ..llm.request import _build_direct_prompt, _build_function_prompt, _build_prompt
    from ..types import GateFacts
    name = "prompt ablation"
    ev = _fw_evidence()
    ws = Path("/tmp/ws/fw.c")
    base = GateFacts(require_speedup=True, n_inputs=2, numeric=False, stress=True)
    marks = {                                        # a phrase only that part contains
        "contract": "THE CONTRACT",
        "gate": "HOW YOUR REWRITE IS CHECKED",
        "granularity": "decides granularity",
        "checklist": "Worth settling before you write",
    }
    if set(marks) != set(PROMPT_PARTS):
        return Result(name, "fail", f"the check knows {sorted(marks)}, the agent {sorted(PROMPT_PARTS)}")
    problems: List[str] = []

    def whole(g: GateFacts, pragmas: bool, mode: str) -> str:
        req = (_build_direct_prompt(ev, ws, None, pragmas, g) if mode == "direct"
               else _build_function_prompt(ev, None, pragmas, g) if mode == "function"
               else _build_prompt(ev, None, pragmas, g))
        return " ".join((_system_prompt(mode, pragmas, False, g) + "\n" + req).split())

    for pragmas in (False, True):
        for mode in ("direct", "function", "diff"):
            full = whole(base, pragmas, mode)
            for part, phrase in marks.items():
                if phrase not in full:
                    problems.append(f"{mode}/{pragmas}: the full prompt lacks {phrase!r}")
                cut = whole(dataclasses.replace(base, omit=(part,)), pragmas, mode)
                if phrase in cut:
                    problems.append(f"{mode}/{pragmas}: --prompt-omit {part} left {phrase!r} in")
                # omitting `gate` takes its closing paragraph (granularity) with it, by design
                for other, other_phrase in marks.items():
                    if other != part and not (part == "gate" and other == "granularity") \
                            and other_phrase not in cut:
                        problems.append(f"{mode}/{pragmas}: --prompt-omit {part} also removed {other}")
            # without the contract the pragma MODE must still be stated
            cut = whole(dataclasses.replace(base, omit=("contract",)), pragmas, mode)
            rule = "Annotate what you parallelize" if pragmas else "Do not write `#pragma omp` yourself"
            if rule not in cut:
                problems.append(f"{mode}/{pragmas}: without the contract the pragma rule is gone")

    remark = "loop not vectorized: unsafe dependent memory operations in loop"
    g_ext = dataclasses.replace(base, external_evidence=f"fw.c:12:3: remark: {remark}")
    for mode in ("direct", "function", "diff"):
        req = (_build_direct_prompt(ev, ws, set(), False, g_ext) if mode == "direct"
               else _build_function_prompt(ev, set(), False, g_ext) if mode == "function"
               else _build_prompt(ev, set(), False, g_ext))
        flat = " ".join(req.split())
        if remark not in flat or "NOT measured" not in flat:
            problems.append(f"{mode}: the external remarks (or their label) are missing")
        for leak in ("Runtime data dependences", "RAW", "measured runtime"):
            if leak in flat:
                problems.append(f"{mode}: --evidence none with an evidence file still shows {leak!r}")
    if problems:
        return Result(name, "fail", "; ".join(problems[:4]) + (f" (+{len(problems) - 4} more)" if len(problems) > 4 else ""))
    return Result(name, "pass",
                  "each of 4 parts removed alone in 3 edit modes x 2 pragma modes, the pragma rule kept "
                  "without the contract; external remarks shown and labelled, no DiscoPoP data beside them")


def check_bare_llm(work: Path) -> Result:
    """The bare-LLM baseline shows the model NOTHING of DiscoPoP's, promises no gate, and keeps
    whatever the model leaves.  A stand-in for the client edits the working copy, so the
    wiring is tested without a model call."""
    name = "bare-LLM baseline"
    import contextlib
    import io
    from .. import bare_llm

    sub = work / "bare"
    sub.mkdir(parents=True, exist_ok=True)
    src = sub / "k.c"
    src.write_text("#include <stdio.h>\nvoid kernel(double*a,int n){for(int i=0;i<n;i++)a[i]*=2;}\n"
                   "int main(void){double a[8]={0};kernel(a,8);printf(\"%f\\n\",a[0]);return 0;}\n")
    (sub / "k.h").write_text("/* a header the model may read */\n")
    seen: Dict[str, Any] = {}

    def fake(model: str, system: str, current: List[Any], session_key: str,
             workspace: Optional[Path] = None, stateless: bool = False) -> str:
        seen.update(system=system, request=current[-1]["content"], stateless=stateless,
                    files=sorted(f.name for f in Path(str(workspace)).iterdir()))
        f = Path(str(workspace)) / "k.c"
        f.write_text(f.read_text().replace("for(int i", "#pragma omp parallel for\nfor(int i"))
        return "Plan: the loop is independent."

    saved, saved_argv = getattr(bare_llm, "_complete_claude_agent_sdk"), sys.argv
    setattr(bare_llm, "_complete_claude_agent_sdk", fake)
    problems: List[str] = []
    prompts: Dict[str, Any] = {}
    try:
        for mode in ("mirror", "minimal", "contract"):
            src.write_text(src.read_text().replace("#pragma omp parallel for\n", ""))
            seen.clear()
            sys.argv = ["bare_llm", "--project-dir", str(sub), "--project-units", "k.c", "--model", "m",
                        "--exclude-functions", "main", "--prompt", mode]
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = bare_llm.main()
            prompts[mode] = (" ".join(seen.get("system", "").split()), " ".join(seen.get("request", "").split()))
            if rc != 0 or "#pragma omp parallel for" not in src.read_text():
                problems.append(f"{mode}: the model's edit was not copied back")
            if "k.h" not in seen.get("files", []):
                problems.append(f"{mode}: the header was not in the model's working copy")
            if "] Calling m" not in out.getvalue():
                problems.append(f"{mode}: the call is not logged in the form the harness counts")
            if not seen.get("stateless"):
                problems.append(f"{mode}: the call is not stateless")
            # the mirror names ThreadSanitizer as part of how the FINISHED program is judged
            leaks = ("HOW YOUR REWRITE IS CHECKED", "DiscoPoP", "re-profiled") + (() if mode == "mirror" else ("ThreadSanitizer",))
            for leak in leaks:
                if leak in prompts[mode][0] or leak in prompts[mode][1]:
                    problems.append(f"{mode}: the bare arm's prompt mentions {leak!r}")
    finally:
        setattr(bare_llm, "_complete_claude_agent_sdk", saved)
        sys.argv = saved_argv
    m_sys, m_req = prompts.get("minimal", ("", ""))
    # D37: nothing of ours that helps — no contract, no rules, no transformation named
    for helper in ("THE CONTRACT", "HEAP-allocated", "reduction(", "private(", "firstprivate", "WHAT OPENMP REQUIRES",
                   "splitting", "buffer", "reordering", "one attempt"):
        if helper.lower() in (m_sys + " " + m_req).lower():
            problems.append(f"minimal: the prompt gives help ({helper!r})")
    if "main" not in m_req or "exactly the same" not in m_req:
        problems.append("minimal: the request lacks the goal or the measuring functions")
    # mirror (the default): the agent's own words where it shares them, nothing of DiscoPoP's
    from ..llm.prompts import (_CONTRACT_PRAGMA, _OMP_RULES, _PLAN_SPEC, _PRAGMA_FORMS, _contract,
                               _system_prompt)
    agent_sys = " ".join(_system_prompt("direct", True, False, bare_llm.MIRROR_GATE).split())
    r_sys, r_req = prompts.get("mirror", ("", ""))
    for label, text in (("the contract", _contract(bare_llm.MIRROR_GATE, _CONTRACT_PRAGMA)),
                        ("the OpenMP rules", _OMP_RULES), ("the pragma forms", _PRAGMA_FORMS),
                        ("the plan request", _PLAN_SPEC)):
        flat = " ".join(text.split())
        if flat not in agent_sys or flat not in r_sys:
            problems.append(f"mirror: {label} is not the agent's exact text")
    for q in ("Which dependence is actually blocking this", "Re-derive any bound the old execution order made safe",
              "ANNOTATED BY YOU", "one attempt"):
        if q not in r_sys + " " + r_req:
            problems.append(f"mirror: lacks {q!r}")
    for leak in ("DiscoPoP", "profil", "evidence", "Target region", "splitting a loop", "adding a buffer",
                 "reordering statements", "RAW", "re-profile"):
        if leak.lower() in (r_sys + " " + r_req).lower():
            problems.append(f"mirror: carries {leak!r}")
    if "main" not in r_req:
        problems.append("mirror: the measuring functions are not named")
    c_sys, c_req = prompts.get("contract", ("", ""))
    for phrase in ("THE CONTRACT", "HEAP-allocated"):
        if phrase not in c_sys:
            problems.append(f"contract: lost {phrase!r} (E1-bare must stay reproducible)")
    if "one attempt" not in c_req:
        problems.append("contract: the request lost the single attempt")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass",
                  f"mirror ({len((r_sys + ' ' + r_req).split())} words): the agent's contract, OpenMP rules, pragma "
                  "forms, plan and checklist verbatim, no DiscoPoP / evidence / region / gate-during-the-run; minimal "
                  f"({len((m_sys + ' ' + m_req).split())} words) and contract (E1-bare) reproducible; the edit kept unchecked")


def check_bare_speed_off(work: Path) -> Result:
    """E2-B1 (the author, 26 Sep): the speed check OFF in every arm, the model alone included.

    The mirror's gate was fixed with the speed check on, so a speed-off agent arm and the model
    alone would have been told different goals.  `--no-require-speedup` builds the mirror from a
    speed-off gate: no speed goal, no timing step in how the program is judged, and every shared
    passage the agent's own speed-off text.  The default (speed on) must stay byte for byte what
    E1c's and E2's model alone read — checked against its words here, and against git when built."""
    from .. import bare_llm
    from ..llm.prompts import _CONTRACT_PRAGMA, _OMP_RULES, _PRAGMA_FORMS, _contract, _system_prompt
    from ..llm.request import _task_checklist
    name = "bare speed off"
    files, excl = ["s000.c"], ["main", "pb_mix"]
    on, off = bare_llm.mirror_gate(True), bare_llm.mirror_gate(False)
    s_on, r_on = bare_llm._system("mirror", on), bare_llm._request_mirror(files, excl, gate=on)
    s_off, r_off = bare_llm._system("mirror", off), bare_llm._request_mirror(files, excl, gate=off)
    problems: List[str] = []
    if (s_on, r_on) != (bare_llm._system("mirror"), bare_llm._request_mirror(files, excl)):
        problems.append("the default mirror is no longer the speed-on mirror")
    for q in ("measurably faster than the original sequential program", "has to be faster"):
        if q not in s_on + r_on:
            problems.append(f"speed on: lost {q!r}")
        if q in s_off + r_off:
            problems.append(f"speed off: still says {q!r}")
    stray = [m for m in re.findall(r"[^.\n]*faster[^.\n]*", s_off + r_off) if "faster serial algorithm" not in m]
    if stray:
        problems.append(f"speed off: a speed goal left: {stray[0].strip()[:70]!r}")
    agent_off = " ".join(_system_prompt("direct", True, False, off).split())
    flat_off = " ".join(s_off.split())
    for label, text in (("the contract", _contract(off, _CONTRACT_PRAGMA)), ("the OpenMP rules", _OMP_RULES),
                        ("the pragma forms", _PRAGMA_FORMS)):
        flat = " ".join(text.split())
        if flat not in agent_off or flat not in flat_off:
            problems.append(f"speed off: {label} is not the agent's speed-off text")
    if " ".join(_task_checklist(off, set()).split()) not in " ".join(r_off.split()):
        problems.append("speed off: the checklist is not the agent's speed-off checklist")
    if problems:
        return Result(name, "fail", "; ".join(problems[:3]))
    return Result(name, "pass", f"speed off: no speed goal or timing step ({len((s_off + r_off).split())} words), "
                  "contract, OpenMP rules, pragma forms and checklist the agent's own speed-off text; "
                  "speed on unchanged")


def check_workspace_confined(work: Path) -> Result:
    """The model's file tools reach its workspace and nothing else (23 Sep).  Listing Read /
    Edit / Write whole in allowed_tools auto-approves them for ANY path, so the confinement is a
    PreToolUse hook: absolute paths outside, `..`, and a symlink leading out are denied; files
    inside are allowed.  Shell, web and search tools are blocked outright."""
    name = "workspace confined"
    import asyncio
    from ..llm.providers import BLOCKED_TOOLS, confine_to
    ws = work / "ws_confine"
    outside = work / "outside_secret"
    ws.mkdir(parents=True, exist_ok=True)
    outside.mkdir(parents=True, exist_ok=True)
    (ws / "k.c").write_text("int main(void){return 0;}\n")
    (outside / "answer.c").write_text("/* the solution */\n")
    link = ws / "escape"
    if not link.exists():
        link.symlink_to(outside)
    hook = confine_to(ws)
    ref = Path(__file__).resolve().parents[2] / "evaluation" / "agent" / "reference_solutions" / "tsvc" / "s211.c"
    cases = [("Read", {"file_path": "k.c"}, True), ("Read", {"file_path": str(ws / "k.c")}, True),
             ("Edit", {"file_path": str(ws / "k.c")}, True),
             ("Read", {"file_path": str(outside / "answer.c")}, False),
             ("Read", {"file_path": "../outside_secret/answer.c"}, False),
             ("Read", {"file_path": "escape/answer.c"}, False),
             ("Read", {"file_path": str(ref)}, False), ("Write", {"file_path": "/tmp/x.c"}, False),
             ("Glob", {"pattern": "*.c", "path": str(outside)}, False)]
    problems: List[str] = []
    for tool, tin, allowed in cases:
        out = asyncio.run(hook({"tool_name": tool, "tool_input": tin}, None, {"signal": None}))
        denied = (out.get("hookSpecificOutput") or {}).get("permissionDecision") == "deny"
        if denied == allowed:
            problems.append(f"{tool} {tin}: {'denied' if denied else 'allowed'}")
    for t in ("Bash", "WebFetch", "WebSearch", "Task", "Grep", "Glob"):
        if t not in BLOCKED_TOOLS:
            problems.append(f"{t} is not blocked")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", f"{len(cases)} paths judged right (outside, `..`, symlink, reference "
                  "solutions denied; the workspace allowed); shell, web and search blocked")


def _section(text: str, title: str) -> str:
    """One `_RULE`-headed block of a system prompt, flattened; '' if absent."""
    from ..llm.prompts import _RULE
    head = _RULE + title + "\n" + _RULE
    if head not in text:
        return ""
    body = text.split(head, 1)[1]
    nxt = body.find(_RULE)
    return " ".join((head + (body if nxt < 0 else body[:nxt])).split())


def check_twin_prompt(work: Path) -> Result:
    """D38 — the twin's prompt is the agent's, less exactly the gate during the run and feedback.

    For both pragma modes, full and no evidence, and with the speed check on and off: the
    agent's system prompt with (a) its "HOW YOUR REWRITE IS CHECKED" block swapped for the
    twin's "HOW YOUR REWRITE IS JUDGED", (b) the clause promising feedback after a failed
    attempt removed, (c) the sentence about edits from an earlier turn removed and (d) the
    one-thread speed goal read as the original sequential program, must equal the twin's —
    nothing else may differ.  The request is the agent's own, with (d) only."""
    import dataclasses
    from .. import twin
    from ..llm.prompts import _system_prompt
    from ..llm.request import _build_direct_prompt
    from ..types import GateFacts
    name = "twin prompt"
    ev = _fw_evidence()
    ws = Path("/tmp/ws/fw.c")
    base = GateFacts(require_speedup=True, n_inputs=2, numeric=False, stress=True)
    flat = lambda t: " ".join(t.split())                                      # noqa: E731
    problems: List[str] = []
    n = 0
    for pragmas in (False, True):
        includes: List[Optional[Set[str]]] = [None, set()]
        for include in includes:
            for g in (base, dataclasses.replace(base, require_speedup=False),
                      dataclasses.replace(base, numeric=True, stress=False)):
                n += 1
                tag = f"{'model' if pragmas else 'DiscoPoP'} pragmas/{'full' if include is None else 'none'}/" \
                      f"{'speed' if g.require_speedup else 'no speed'}{'/numeric' if g.numeric else ''}"
                agent = _system_prompt("direct", pragmas, False, g, include)
                mine = twin._system(g, include, pragmas)
                checked = _section(agent, "HOW YOUR REWRITE IS CHECKED")
                judged = _section(mine, "HOW YOUR REWRITE IS JUDGED")
                if not checked or not judged:
                    problems.append(f"{tag}: a gate block is missing")
                    continue
                expect = (flat(agent).replace(checked, judged)
                          .replace(" — and, " + twin.FEEDBACK_CLAUSE + ".", ".")
                          .replace(" and, " + twin.FEEDBACK_CLAUSE + ".", ".")
                          .replace(flat(twin.EARLIER_TURN), "").replace("  ", " ")
                          .replace(*twin.SPEED_GOAL_ANNOTATE))
                if flat(expect) != flat(mine):
                    a, b = flat(expect), flat(mine)
                    k = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), min(len(a), len(b)))
                    problems.append(f"{tag}: differs beyond the gate at …{b[max(0, k - 40):k + 40]!r}")
                for must in ("Nothing checks your work while you do it", "one attempt", "ThreadSanitizer"):
                    if must not in judged:
                        problems.append(f"{tag}: the judged block lacks {must!r}")
                for gone in ("after a failed attempt", "earlier turn", "read statically",
                             "or the rewrite is reverted", "pinned to one thread", "held to one thread"):
                    if gone in flat(mine):
                        problems.append(f"{tag}: the twin still says {gone!r}")
                if g.require_speedup != ("original sequential" in judged):
                    problems.append(f"{tag}: the timing step does not follow the speed check")
                if not pragmas and "DiscoPoP re-profiles the program as you leave it" not in judged:
                    problems.append(f"{tag}: the twin is not told DiscoPoP annotates afterwards")
                req = _build_direct_prompt(ev, ws, include, pragmas, g)
                mine_req = twin._request(req)
                want = req.replace(*twin.SPEED_ONE_THREAD)
                if mine_req != want or (pragmas and g.require_speedup and mine_req == req):
                    problems.append(f"{tag}: the request is not the agent's")
                # D40 (agent v3): the agent now reads the twin's speed words itself, so with
                # judge_as_shipped the twin's texts are the agent's with only (a)-(c) — (d) is gone.
                v3 = dataclasses.replace(g, judge_as_shipped=True)
                agent3 = _system_prompt("direct", pragmas, False, v3, include)
                checked3 = _section(agent3, "HOW YOUR REWRITE IS CHECKED")
                expect3 = (flat(agent3).replace(checked3, judged)
                           .replace(" — and, " + twin.FEEDBACK_CLAUSE + ".", ".")
                           .replace(" and, " + twin.FEEDBACK_CLAUSE + ".", ".")
                           .replace(flat(twin.EARLIER_TURN), "").replace("  ", " "))
                if checked3 and flat(expect3) != flat(mine):
                    problems.append(f"{tag}: with judge_as_shipped the twin differs from the agent beyond the gate")
                if mine_req != _build_direct_prompt(ev, ws, include, pragmas, v3):
                    problems.append(f"{tag}: with judge_as_shipped the twin's request is not the agent's word for word")
    if problems:
        return Result(name, "fail", "; ".join(problems[:3]) + (f" (+{len(problems) - 3} more)" if len(problems) > 3 else ""))
    return Result(name, "pass", f"{n} configurations: the agent's system prompt and request, less only the "
                  "gate during the run, the feedback clause and the earlier-turn sentence")


_TWIN_SRC = """#include <stdio.h>
#define N 20000
static double a[N], b[N], c[N];
void rec(void) {
  double run = 0.0;
  for (int i = 0; i < N; i++) {
    run = run * 0.5 + a[i];
    b[i] = run;
  }
}
void scale(void) {
  for (int i = 0; i < N; i++)
    c[i] = a[i] * 2.0 + 1.0;
}
int main(void) {
  for (int i = 0; i < N; i++) a[i] = (i % 13) * 0.5;
  for (int r = 0; r < 20; r++) { rec(); scale(); }
  double s = 0;
  for (int i = 0; i < N; i++) s += b[i] + c[i];
  printf("%.3f\\n", s);
  return 0;
}
"""


def check_twin_run(work: Path) -> Result:
    """D38 — a twin asks what the agent asks, keeps what the model leaves, re-profiles, and
    lets DiscoPoP annotate with nothing checked.

    A recurrence (`rec`, which DiscoPoP cannot parallelize) beside a clean Do-All (`scale`).
    The agent is run with the arm's arguments up to its first model call, and stopped there;
    the twin is run with the same arguments.  Its first request must be the agent's (the
    working-copy path aside); the stand-in model rewrites the recurrence into an independent
    loop; the twin must keep that edit unchecked, re-profile, and insert DiscoPoP's pragma for
    BOTH loops without any gate — and save the program as the model left it.  With
    `--budget 0` (the twin of DiscoPoP alone) no model is called and DiscoPoP's pragma for
    `scale` goes in unchecked."""
    name = "twin run"
    import contextlib
    import io
    if not Path(_venv_bin("discopop_cxx")).exists():
        return Result(name, "skip", "DiscoPoP is not installed in this venv")
    import importlib
    from .. import twin
    from ..args import parse_args
    from ..llm.request import _build_direct_prompt
    # the modules, not the functions the packages re-export under the same names
    agent_run: Any = importlib.import_module("discopop_agent.run")
    phase_a: Any = importlib.import_module("discopop_agent.phases.phase_a")
    twin_mod: Any = twin
    d = work / "twin_run"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    (d / "k.cpp").write_text(_TWIN_SRC)
    ok, err = _profile(d, "k.cpp")
    if not ok:
        return Result(name, "fail", f"profile: {err}")
    base_argv = ["x", "--discopop-dir", str(d / ".discopop"), "--source-file", str(d / "k.cpp"),
                 "--provider", "claude-agent-sdk", "--model", "m", "--edit-mode", "direct",
                 "--exclude-functions", "main", "--no-require-speedup", "--budget", "1"]
    seen: Dict[str, Any] = {}

    class Stop(BaseException):
        pass

    def agent_call(evidence: Any, model: str, **kw: Any) -> Any:
        seen["agent"] = _build_direct_prompt(evidence, Path("/WS/k.cpp"), kw.get("evidence_sections"),
                                             kw.get("llm_pragmas", False), kw["gate"])
        raise Stop()

    calls: List[str] = []

    def model(provider: str, client: Any, model_name: str, current: List[Any], system: str,
              session_key: str = "", workspace: Optional[Path] = None, stateless: bool = False) -> str:
        f = Path(str(workspace)) / "k.cpp"
        calls.append(current[-1]["content"].replace(str(f), "/WS/k.cpp"))
        seen["system"], seen["stateless"] = system, stateless
        f.write_text(f.read_text().replace("run = run * 0.5 + a[i];\n    b[i] = run;", "b[i] = a[i] * 0.5 + a[i];"))
        return "Plan: b no longer depends on the previous iteration."

    saved_argv = sys.argv
    saved_call, saved_complete = phase_a.call_llm, twin_mod._complete
    problems: List[str] = []
    log = io.StringIO()
    try:
        phase_a.call_llm = agent_call
        sys.argv = base_argv
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                agent_run.run(parse_args())
        except Stop:
            pass
        twin_mod._complete = model
        with contextlib.redirect_stdout(log):
            rc = twin.run(parse_args())
        final = (d / "k.cpp").read_text()
        before = d / ".discopop" / "agent_patches" / "twin_model_program.cpp"
        if rc != 0:
            problems.append(f"the twin exited {rc}")
        if "agent" not in seen:
            problems.append("the agent never reached a model call")
        elif not calls or " ".join(calls[0].split()) != " ".join(seen["agent"].split()):
            problems.append("the twin's first request is not the agent's")
        elif "run = run * 0.5" not in calls[0]:
            problems.append("the model was not asked about the recurrence")
        if not seen.get("stateless"):
            problems.append("the call is not stateless (one attempt)")
        if "a[i] * 0.5 + a[i]" not in final:
            problems.append("the model's edit was not kept")
        if final.count("#pragma omp parallel for") < 2:
            problems.append(f"DiscoPoP inserted {final.count('#pragma omp parallel for')} pragma(s), not 2 "
                            "(the rewritten loop and scale)")
        if not before.exists() or "#pragma omp" in before.read_text() \
                or "a[i] * 0.5 + a[i]" not in before.read_text():
            problems.append("the program as the model left it was not saved before annotation")
        text = log.getvalue()
        for gate_word in ("Quality gate", "ThreadSanitizer", "Stage '", "SETTLING", "marginal", "[floor]"):
            if gate_word in text:
                problems.append(f"the twin ran a gate step ({gate_word!r})")
        if "] Calling m" not in text or "INSERTED (unchecked)" not in text or "Re-profiling" not in text:
            problems.append("the log lacks the call, the re-profile or the unchecked insertion")
        # DiscoPoP alone, unchecked: the twin of --budget 0
        (d / "k.cpp").write_text(_TWIN_SRC)
        ok, err = _profile(d, "k.cpp")
        n_before = len(calls)
        sys.argv = base_argv[:-1] + ["0"]
        with contextlib.redirect_stdout(io.StringIO()):
            twin.run(parse_args())
        final0 = (d / "k.cpp").read_text()
        if len(calls) != n_before:
            problems.append("--budget 0 called the model")
        if final0.count("#pragma omp parallel for") != 1 or "run = run * 0.5" not in final0:
            problems.append(f"--budget 0: expected DiscoPoP's one pragma on scale, got "
                            f"{final0.count('#pragma omp parallel for')}")
    finally:
        phase_a.call_llm = saved_call
        twin_mod._complete = saved_complete
        sys.argv = saved_argv
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", f"{len(calls)} call(s); the first request is the agent's; the edit kept unchecked, "
                  "re-profiled, DiscoPoP's pragmas inserted with no gate step; budget 0 = DiscoPoP alone unchecked")


_HARNESS_SRC = """#include "tsvc/s000.h"

static void pb_mix(int nl)
{
  long k = ((long)nl * 7919L + 13L) % LEN_1D;
  a[k] += (real_t)0.25;
}

static real_t kernel_s000(void)
{
    for (int nl = 0; nl < R; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = b[i] + 1;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s000)
"""
_HARNESS_PROTECTED = ('#include "tsvc/s000.h"', "static void pb_mix(int nl)",
                      "long k = ((long)nl * 7919L + 13L) % LEN_1D;", "a[k] += (real_t)0.25;",
                      "pb_mix(nl);", "PB_MAIN(kernel_s000)")


def check_harness_lines(work: Path) -> Result:
    """Fix 97 (D39): the lines a benchmark shares with its measurement harness.

    The gate's `harness` stage refuses a candidate that changes, drops, moves or duplicates one
    of them — the E1c `s313` case, where the model inlined `pb_mix` into the kernel — and lets
    every other change through (a pragma, a restructured loop, re-indentation). Every arm is
    told about them in the same words: the block appears verbatim in the agent's three request
    forms, in its twin's request and in the model alone's."""
    name = "harness lines"
    from .. import bare_llm, twin
    from ..gate.harness_lines import check_protected
    from ..llm.request import _build_direct_prompt, _build_function_prompt, _build_prompt, _protected_block
    from ..types import GateFacts
    d = work / "harness_lines"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "s000.c"
    src.write_text(_HARNESS_SRC)
    P = _HARNESS_PROTECTED

    def diff_to(new: str) -> str:
        return make_diff(_HARNESS_SRC, new, str(src))

    good = {
        "a pragma on the loop": _HARNESS_SRC.replace("        for (int i = 0;", "        #pragma omp parallel for\n        for (int i = 0;"),
        "a restructured body": _HARNESS_SRC.replace("a[i] = b[i] + 1;", "a[i] = 1 + b[i];"),
        "re-indented harness lines": _HARNESS_SRC.replace("        pb_mix(nl);", "            pb_mix(nl);"),
    }
    bad = {
        "pb_mix inlined (the s313 case)": _HARNESS_SRC.replace("        pb_mix(nl);", "        a[((long)nl * 7919L + 13L) % LEN_1D] += (real_t)0.25;"),
        "pb_mix's body edited": _HARNESS_SRC.replace("a[k] += (real_t)0.25;", "a[k] += (real_t)0.5;"),
        "pb_mix called twice": _HARNESS_SRC.replace("        pb_mix(nl);", "        pb_mix(nl);\n        pb_mix(nl);"),
        "pb_mix moved before the loop": _HARNESS_SRC.replace("        pb_mix(nl);\n", "").replace(
            "    for (int nl = 0; nl < R; nl++) {\n", "    for (int nl = 0; nl < R; nl++) {\n        pb_mix(nl);\n"),
        "the include removed": _HARNESS_SRC.replace('#include "tsvc/s000.h"\n', ""),
    }
    problems: List[str] = []
    for label, text in good.items():
        why = check_protected(diff_to(text), str(src), P)
        if why:
            problems.append(f"refused {label}: {why[:80]}")
    for label, text in bad.items():
        if not check_protected(diff_to(text), str(src), P):
            problems.append(f"let through {label}")
    if check_protected(diff_to(bad["pb_mix inlined (the s313 case)"]), str(src), ()):
        problems.append("a package without protected lines is checked anyway")

    note = "`pb_mix(nl)` changes a few input values between two repetitions."
    g = GateFacts(require_speedup=True, n_inputs=2, numeric=False, stress=True, protected=P, protected_note=note)
    block = _protected_block(g)
    ev = _fw_evidence()
    reqs = {"direct": _build_direct_prompt(ev, Path("/tmp/ws/fw.c"), None, False, g),
            "function": _build_function_prompt(ev, None, False, g),
            "diff": _build_prompt(ev, None, False, g),
            "twin": twin._request(_build_direct_prompt(ev, Path("/tmp/ws/fw.c"), None, True, g)),
            "model alone": bare_llm._request_mirror(["s000.c"], ["main", "pb_mix"], P, note)}
    for who, text in reqs.items():
        if block not in text:
            problems.append(f"{who}: the block is not there verbatim")
    if "Do not change these functions" in reqs["model alone"]:
        problems.append("model alone: still told what the agent is not (the old sentence)")
    if "Do not change these functions" not in bare_llm._request_mirror(["s000.c"], ["main", "pb_mix"]):
        problems.append("model alone on a v3 package: the old sentence is gone (E1c must stay reproducible)")
    if _protected_block(GateFacts()) != "":
        problems.append("a package without protected lines gets a block")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", f"{len(good)} legitimate changes through, {len(bad)} harness edits refused "
                  "(inlined, edited, duplicated, moved, include dropped); the same block in the agent's 3 request "
                  "forms, the twin's and the model alone's; v3 packages unchanged")


def check_covered_skip(work: Path) -> Result:
    """A region inside an already-accepted one must leave the queue.

    Once a region is parallelised, `ImpactModel.mark_covered` sets the predicted
    saving of everything nested inside it to 0. The queue used to drop a region
    only when its saving was BELOW `--min-impact` (default 0), so a saving of
    exactly 0 passed and every covered region still received a full model budget.
    """
    name = "covered skip"
    dp = work / ".discopop"
    src = str(work / "priority_mix.cpp")
    if not (dp / "hotspot_detection" / "Hotspots.json").exists():
        return Result(name, "skip", "needs the impact-ranking profile")
    model = load_hotspots(dp, threads=8)
    before = build_candidates(dp, src, 1.0, 0.0, impact=model, min_impact=0.0)
    loops = [c for c in before if c.region.region_type == "loop" and c.impact_seconds]
    if not loops:
        return Result(name, "skip", "no measured loop to cover")
    outer = max(loops, key=lambda c: (c.region.end_line - c.region.start_line, c.impact_seconds or 0.0))
    r = outer.region

    def inside(c: HotspotCandidate) -> bool:
        return bool(c.region.file_id == r.file_id and r.start_line <= c.region.start_line
                and c.region.end_line <= r.end_line)

    nested = [c for c in before if inside(c)]
    model.mark_covered(r.file_id, r.start_line, r.end_line)
    after = build_candidates(dp, src, 1.0, 0.0, impact=model, min_impact=0.0)
    left = [c for c in after if inside(c) and c.impact_seconds is not None]
    outside_before = [c for c in before if not inside(c)]
    outside_after = [c for c in after if not inside(c)]
    if left:
        return Result(name, "fail", f"{len(left)} covered region(s) still queued, e.g. "
                                    f"{left[0].region.region_id} saving {left[0].impact_seconds}")
    if len(outside_after) != len(outside_before):
        return Result(name, "fail", f"regions outside the covered span changed: "
                                    f"{len(outside_before)} -> {len(outside_after)}")
    return Result(name, "pass", f"covering lines {r.start_line}–{r.end_line} removed "
                                f"{len(nested)} region(s); {len(outside_after)} outside it kept")


def check_budget_policy(work: Path) -> Result:
    """--budget-policy share scales attempts with runtime share; fixed is unchanged."""
    from ..plan import region_budget
    name = "budget policy"
    cases = [
        (("fixed", 3, 1, 0.05, 1.0), 3),   # fixed ignores the share
        (("fixed", 0, 1, 1.0, 1.0), 0),    # discopop_gate: no calls under either policy
        (("share", 0, 1, 1.0, 1.0), 0),
        (("share", 5, 1, 1.0, 1.0), 5),    # the largest share gets the maximum
        (("share", 5, 1, 0.5, 1.0), 3),
        (("share", 5, 1, 0.01, 1.0), 1),   # a small share gets the minimum
        (("share", 5, 1, None, 1.0), 1),   # unmeasured: the minimum
        (("share", 5, 1, 0.3, 0.6), 3),    # relative to the largest queued share
        (("share", 3, 1, 2.0, 1.0), 3),    # never above the maximum
    ]
    bad = [f"{a} -> {region_budget(*a)} (want {w})" for a, w in cases if region_budget(*a) != w]
    if bad:
        return Result(name, "fail", "; ".join(bad))
    return Result(name, "pass", f"{len(cases)} cases: fixed unchanged, share from min to max, "
                                f"unmeasured at min, zero budget stays zero")


def _fw_evidence() -> "EvidencePackage":
    """Floyd–Warshall's kernel as the agent sees it, written out by hand so the prompt
    checks need no profile: three loops of 32 iterations, RAW on the array, and the
    induction-variable and signature-line entries DiscoPoP really reports with it."""
    from ..types import Dependency, EvidencePackage
    text = {414: "void kernel_floyd_warshall(int n,", 415: "\t\t\t   double path[N][N])", 416: "{",
            417: "  int i, j, k;", 418: "  for (k = 0; k < n; k++)", 419: "    {",
            420: "      for(i = 0; i < n; i++)", 421: "\tfor (j = 0; j < n; j++)",
            422: "\t  path[i][j] = path[i][j] < path[i][k] + path[k][j] ?",
            423: "\t    path[i][j] : path[i][k] + path[k][j];", 424: "    }", 425: "}"}
    raw = [Dependency("RAW", 422, 422, "path", "array"), Dependency("RAW", 423, 422, "path", "array"),
           Dependency("RAW", 422, 414, "path", "array"), Dependency("RAW", 422, 418, "k"),
           Dependency("RAW", 422, 421, "j"), Dependency("RAW", 422, 420, "i"),
           Dependency("RAW", 418, 414, "n")]
    nest = [{"start": 418, "end": 424, "depth": 0, "index_vars": ["k"], "entries": 1, "avg": 32, "total": 32, "max": 32},
            {"start": 420, "end": 423, "depth": 1, "index_vars": ["i"], "entries": 32, "avg": 32, "total": 1024, "max": 32},
            {"start": 421, "end": 423, "depth": 2, "index_vars": ["j"], "entries": 1024, "avg": 32, "total": 32768, "max": 32}]
    return EvidencePackage(
        region_id="1:68", region_type="function", start_line=414, end_line=425,
        source_file="/tmp/fw.c",
        source_region="\n".join(f"{k:4d} >>> {text[k]}" for k in sorted(text)), iteration_count=1,
        raw_deps=raw, war_deps=[Dependency("WAR", 420, 420, "i")], waw_deps=[], reduction_vars=[],
        tier1_failure_reason="DiscoPoP found no applicable parallelism pattern for this region",
        loop_nest=nest, line_text=text, enclosing_function_name="kernel_floyd_warshall",
        enclosing_function_start=414, enclosing_function_end=425,
        enclosing_function_source="\n".join(text[k] for k in sorted(text)),
        array_accesses={"path": {"writes": ["[i][j]"], "reads": ["[i][j]", "[i][k]", "[k][j]"]}},
        inner_patterns=[], runtime_share=0.97)


def check_prompt_truth(work: Path) -> Result:
    """The prompt describes the gate that runs and the evidence that is sent.

    Found by rendering a real prompt and reading it as the model does (review
    P2-P5, P9).  It promised a timing step that is off in every arm, "byte for
    byte" where a measured tolerance applies, and a re-profile that does not
    happen in the default mode; it branded every loop "too fine-grained" at the
    profiling size; and `--evidence none`, the arm the evidence claim is measured
    against, still opened with DiscoPoP's dependence digest.
    """
    from ..llm.prompts import _system_prompt
    from ..llm.request import _build_direct_prompt, _build_function_prompt, _build_prompt
    from ..types import GateFacts
    name = "prompt truth"
    ev = _fw_evidence()
    ws = Path("/tmp/ws/fw.c")
    campaign = GateFacts(require_speedup=False, n_inputs=2, numeric=True, stress=True)
    strict = GateFacts(require_speedup=True, n_inputs=1, numeric=False, stress=False)
    problems: List[str] = []

    def need(text: str, present: List[str], absent: List[str], what: str) -> None:
        flat = " ".join(text.split())
        problems.extend(f"{what}: missing {x!r}" for x in present if x not in flat)
        problems.extend(f"{what}: still says {x!r}" for x in absent if x in flat)

    # 0. The platform constraint is UNCONDITIONAL. It first went into the branch that only
    # runs under a numeric tolerance, so the default configuration never saw it and the model
    # wrote an 8 MB array on the stack twice (e1_smoke, e1_smoke2). Every mode, every gate.
    for pragmas in (True, False):
        for g, label in ((campaign, "campaign gate"), (strict, "strict gate")):
            need(_system_prompt("direct", pragmas, False, g),
                 ["HEAP-allocated", "stack is 8 MB"], [],
                 f"memory constraint, llm_pragmas={pragmas}, {label}")

    # 1. The system prompt follows the gate — in both pragma modes.
    need(_system_prompt("direct", True, False, campaign),
         ["Speed is NOT judged", "2 different inputs", "guided schedules", "rounding",
          "within a constant factor", "O(n^2)"],
         ["has to be faster", "byte for byte", "byte-identical", "measurably faster"],
         "default mode, campaign gate")
    need(_system_prompt("direct", True, False, strict),
         ["has to be faster", "byte for byte", "byte-identical", "measurably faster"],
         ["Speed is NOT judged", "guided schedules", "different inputs"],
         "default mode, strict gate")
    need(_system_prompt("diff", False, False, campaign),
         ["re-profiled", "Speed is NOT judged", "Do not write `#pragma omp`"],
         ["faster than the sequential build", "speed against", "byte for byte"],
         "DiscoPoP-annotates mode, campaign gate")
    need(_system_prompt("diff", False, False, strict),
         ["faster than the sequential build", "speed against the same build"], [],
         "DiscoPoP-annotates mode, strict gate")
    if _system_prompt("direct", True, False, campaign) != _system_prompt("direct", True, False, campaign):
        problems.append("the system prompt is not byte-identical across calls (prompt cache would miss)")

    # 2. The task says what the running mode does, in every edit mode.
    for label, build in (("direct", lambda lp, g, inc: _build_direct_prompt(ev, ws, inc, lp, g)),
                         ("function", lambda lp, g, inc: _build_function_prompt(ev, inc, lp, g)),
                         ("diff", lambda lp, g, inc: _build_prompt(ev, inc, lp, g))):
        need(build(True, campaign, None), ["ANNOTATED BY YOU", "Nothing re-profiles"],
             ["after re-profiling", "measurable speedup", "faster than"], f"{label} task, model annotates")
        need(build(False, strict, None), ["after re-profiling", "measurable speedup",
                                          "Do not write `#pragma omp`"], ["ANNOTATED BY YOU"],
             f"{label} task, DiscoPoP annotates")
        # 3. --evidence none is the source and the task: nothing DiscoPoP measured.
        bare = build(True, campaign, set())
        need(bare, ["path[i][j]"],
             ["Evidence digest", "RAW", "activation", "Do-All blockers", "32 iterations",
              "accounts for", "written as"], f"{label} prompt under --evidence none")
    import dataclasses
    loop_ev = dataclasses.replace(ev, region_type="loop", iteration_count=32768)
    need(_build_prompt(loop_ev, set(), True, campaign), [], ["32,768"],
         "diff header of a loop region under --evidence none")
    need(_system_prompt("direct", True, False, campaign, set()), ["No profiling data"],
         ["dependences observed at run time", "Do-All blockers"], "system prompt under --evidence none")

    # 4. Granularity is only marked when speed is really judged at this size.
    full = _build_direct_prompt(ev, ws, None, True, campaign)
    need(full, ["deliberately small profiling input"], ["too fine-grained"], "loop structure, speed off")
    need(_build_direct_prompt(ev, ws, None, True, strict), ["too fine-grained"], [], "loop structure, speed on")

    # 5. Signal before noise: no induction variables, no signature line, arrays named as arrays.
    need(full, ["ARRAY ELEMENTS of: path", "path [array element]", "written as [i][j]",
                "[i][k], [k][j]", "private(...)", "about 97%", "Why this region is here"],
         ["RAW on SCALARS", "422→414", "418→414", "k [scalar]", "What went wrong"], "evidence body")
    if problems:
        return Result(name, "fail", "; ".join(problems[:6]) + (f" (+{len(problems) - 6} more)" if len(problems) > 6 else ""))
    return Result(name, "pass", "system prompt and task follow the gate and the pragma mode in all three "
                                "edit modes; --evidence none carries no DiscoPoP data; no granularity "
                                "verdict without a speed check; induction and signature noise dropped")


_ENRICH_SRC = (
    "#include <stdio.h>\n#define R 300\n#define T 40\n"
    "static double a[R][T];\nstatic double b[R];\n"
    "void kernel(int n)\n{\n  int i, t;\n"
    "  for (i = 0; i < n; i++)\n    for (t = 1; t < T; t++)\n"
    "      a[i][t] = a[i][t-1] * 0.5 + 1.0;\n"
    "  for (i = 1; i < n; i++)\n    b[i] = b[i-1] + a[i][T-1];\n}\n"
    "int main(void) {\n  int i;\n"
    "  for (i = 0; i < R; i++) { a[i][0] = 1.0 + (i % 17) * 0.25; b[i] = 0.0; }\n"
    "  kernel(R);\n  printf(\"%.10f\\n\", b[R-1]);\n  return 0;\n}\n")


def check_evidence_enrichment(work: Path) -> Result:
    """Arrays are recognised in C, and the evidence carries what the source shows.

    DiscoPoP marks an array access with a `GEPRESULT_` prefix in C++ and names it
    plainly in C, so every array of the 30 PolyBench kernels reached the model
    tagged [scalar] (review P1).  The access summary (P6) and the loops DiscoPoP
    already reports parallel inside a region (P7) are checked on the same profile.
    """
    import json
    from ..evidence import assemble
    from ..evidence.context import _array_accesses
    name = "evidence enrichment"
    d = work / "enrich"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "kern.c"
    src.write_text(_ENRICH_SRC)
    problems: List[str] = []

    acc = _array_accesses(str(src), 1, len(_ENRICH_SRC.splitlines()))
    if acc.get("a", {}).get("writes") != ["[i][t]", "[i][0]"]:
        problems.append(f"writes of a read as {acc.get('a', {}).get('writes')}")
    if "[i][t-1]" not in acc.get("a", {}).get("reads", []) or "[i-1]" not in acc.get("b", {}).get("reads", []):
        problems.append(f"reads not recognised: {acc}")
    macro = d / "macro.c"
    macro.write_text("void f(int n, double (*A)[8][8]) {\n  int i;\n  for (i = 1; i < n; i++)\n"
                     "    (*A)[i][0] += (*A)[i-1][0];  // A[9] in a comment\n}\n")
    m = _array_accesses(str(macro), 1, 5).get("A", {})
    if m.get("writes") != ["[i][0]"] or sorted(m.get("reads", [])) != ["[i-1][0]", "[i][0]"]:
        problems.append(f"`(*A)[i][0] +=` read as {m}")

    if shutil.which(_venv_bin("discopop_cxx")) is None:
        return Result(name, "fail" if problems else "skip",
                      "; ".join(problems) or "DiscoPoP not installed — source-level parts passed")
    # Profiled twice: as C, where DiscoPoP names arrays plainly, and as C++, where it
    # prefixes and mangles them.  Both have to reach the model as `a` and `b`.
    cxx = work / "enrich_cxx"
    cxx.mkdir(parents=True, exist_ok=True)
    (cxx / "kern.cpp").write_text(_ENRICH_SRC)
    from ..plan.regions import demangle

    def kernel_evidence(root: Path, file: Path) -> "Optional[EvidencePackage]":
        cands = build_candidates(root / ".discopop", str(file), 0.0, min_workload=0.0)
        kern = [c for c in cands if demangle(c.region.name) == "kernel"]
        return assemble(kern[0], root / ".discopop" / "profiler", "") if kern else None

    def judge(ev: "EvidencePackage", lang: str) -> None:
        kinds = {x.variable: x.kind for x in ev.raw_deps + ev.war_deps + ev.waw_deps}
        odd = sorted(v for v in kinds if v.startswith(("_Z", "ZL", "GEP")) or v.endswith("[]"))
        if odd:
            problems.append(f"{lang}: names reach the model as {odd}")
        wrong = sorted(v for v in ("a", "b") if kinds.get(v, "array") != "array")
        if wrong:
            problems.append(f"{lang}: array(s) {wrong} tagged scalar")
        if not {"a", "b"} & set(kinds):
            problems.append(f"{lang}: no dependence on a or b reached the evidence ({sorted(kinds)})")

    ok, err = _profile(cxx, "kern.cpp", hotspots=False)
    if ok:
        ev_cxx = kernel_evidence(cxx, cxx / "kern.cpp")
        if ev_cxx is None:
            problems.append("C++: no function region for `kernel`")
        else:
            judge(ev_cxx, "C++")
    ok, err = _profile(d, src.name, hotspots=False, c_as_c=True)
    if not ok:
        return Result(name, "fail" if problems else "skip", "; ".join(problems) or f"could not profile: {err}")
    dp = d / ".discopop"
    ev_c = kernel_evidence(d, src)
    if ev_c is None:
        return Result(name, "fail", "C: no function region for `kernel`")
    ev = ev_c
    judge(ev, "C")
    if ev.array_accesses.get("b", {}).get("reads") != ["[i-1]"]:
        problems.append(f"access summary of b: {ev.array_accesses.get('b')}")
    pats = json.loads((dp / "explorer" / "patterns.json").read_text())["patterns"]
    want = sorted({int(str(p["start_line"]).split(":")[1]) for k in ("do_all", "reduction")
                   for p in pats.get(k, []) if str(p.get("applicable_pattern")) == "True"
                   and ev.start_line <= int(str(p["start_line"]).split(":")[1]) <= ev.end_line})
    got = sorted(p["line"] for p in ev.inner_patterns)
    if got != want:
        problems.append(f"inner patterns {got}, patterns.json says {want}")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", f"arrays a, b tagged array in C; subscripts read from the source "
                                f"(incl. `(*A)[i][0] +=`); {len(got)} loop(s) already parallel inside "
                                f"`kernel` reported")


def check_pattern_choice(work: Path) -> Result:
    """The pattern that speaks for a loop, and the loops Phase B must not nest into.

    patterns.json lists `task` before `do_all` before `reduction`, and the index
    kept whichever came first — so a task entry (no patch exists for those, and it
    is usually not applicable) hid the loop pattern on the same line, in every arm
    including the DiscoPoP baseline (review F1).  And without runtime measurements
    Phase B could put DiscoPoP's pragma inside a loop the model had already made
    parallel (review F12).
    """
    import json
    from ..plan.regions import _load_pattern_options, _load_patterns
    from ..pragmas import existing_parallel_spans
    name = "pattern choice"
    d = work / "pattern_choice"
    d.mkdir(parents=True, exist_ok=True)
    pj = d / "patterns.json"
    mk = lambda pid, line, ok: {"pattern_id": pid, "start_line": f"1:{line}", "node_id": f"1:{pid + 40}",
                                "applicable_pattern": ok, "pragma": "#pragma omp parallel for"}
    pj.write_text(json.dumps({"patterns": {
        "optimizer_output": [mk(9, 10, True)],
        "task": [mk(1, 10, False), mk(2, 20, True)],
        "do_all": [mk(3, 10, True), mk(4, 20, False), mk(5, 30, True)],
        "reduction": [mk(6, 10, True)]}}))
    from ..plan.regions import line_key, node_key
    best, opts = _load_patterns(pj), _load_pattern_options(pj)
    problems = []
    l10, l20 = line_key(1, 10), line_key(1, 20)
    if best[l10][0] != "reduction":
        problems.append(f"line 10 is represented by {best[l10][0]!r}, want reduction")
    if [t for t, _p in opts[l10]] != ["reduction", "do_all", "task"]:
        problems.append(f"line 10 options ordered {[t for t, _p in opts[l10]]}")
    if best[l20][0] != "task":
        problems.append("an applicable task pattern lost to a non-applicable do_all")
    if any(t == "optimizer_output" for o in opts.values() for t, _p in o):
        problems.append("an aggregate entry was indexed as a pattern")
    if best[node_key("1:43")][1]["pattern_id"] != 3:
        problems.append("node_id lookup does not reach the pattern")
    # Line 43 of file 1 is NOT node 1:43: a region starting there has no pattern.
    if line_key(1, 43) in best:
        problems.append("a node id answered a START-LINE lookup (1:43 as a line)")

    text = ("void f(int n) {\n"                                   # 1
            "  int i, j;\n"                                       # 2
            "  #pragma omp parallel for private(j)\n"             # 3
            "  for (i = 0; i < n; i++)\n"                         # 4
            "    for (j = 0; j < n; j++)\n"                       # 5
            "      a[i][j] = 0;\n"                                # 6
            "  for (i = 0; i < n; i++) b[i] = 0;\n"               # 7
            "  #pragma omp parallel\n"                            # 8
            "  {\n"                                               # 9
            "    work();\n"                                       # 10
            "  }\n"                                               # 11
            "  #pragma omp simd\n"                                # 12
            "  for (i = 0; i < n; i++) c[i] = 0;\n"               # 13
            "}\n")
    spans = existing_parallel_spans(text)
    if spans != [(4, 6), (9, 11)]:
        problems.append(f"parallel spans read as {spans}, want [(4, 6), (9, 11)]")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", "reduction > do_all > task per loop, applicable first, alternates kept; "
                                "parallel loops and blocks located, `simd` and serial loops not")


_PROJ_HEADER = ("#ifndef KERN_H\n#define KERN_H\n#define R 300\n#define T 40\n"
                "extern double a[R][T];\nextern double b[R];\n"
                "void kernel(int n);\nvoid smooth(int n);\n#endif\n")
_PROJ_KERN = ("#include \"kern.h\"\ndouble a[R][T];\ndouble b[R];\n"
              "void kernel(int n)\n{\n  int i, t;\n"
              "  for (i = 0; i < n; i++)\n    for (t = 1; t < T; t++)\n"
              "      a[i][t] = a[i][t-1] * 0.5 + 1.0;\n}\n"
              "void smooth(int n)\n{\n  int i;\n"
              "  for (i = 1; i < n; i++)\n    b[i] = b[i-1] * 0.5 + a[i][T-1];\n}\n")
_PROJ_MAIN = ("#include <stdio.h>\n#include \"kern.h\"\nint main(void) {\n  int i;\n"
              "  for (i = 0; i < R; i++) { a[i][0] = 1.0 + (i % 17) * 0.25; b[i] = 0.0; }\n"
              "  kernel(R);\n  smooth(R);\n  double s = 0.0;\n"
              "  for (i = 0; i < R; i++) s += b[i];\n  printf(\"%.10f\\n\", s);\n  return 0;\n}\n")


def check_project_mode(work: Path) -> Result:
    """A multi-file program: profiled whole, built for real, edited file by file.

    The reason for the unity unit is checked, not assumed: profiled the way
    DiscoPoP documents (unit by unit) this two-file program has BOTH of its
    recurrences reported as applicable Do-All, because loops outside main's unit
    get no loop states; through the unity unit they are blocked, and every region
    still carries its real file and line (docs/MULTIFILE.md).
    """
    import json
    from .. import project as project_mod
    from ..gate import capture_reference
    from ..gate.validate import validate
    from ..profiling import _reprofil
    name = "project mode"
    if shutil.which(_venv_bin("discopop_cc")) is None:
        return Result(name, "skip", "DiscoPoP not installed")
    root = work / "proj"
    (root / "src").mkdir(parents=True, exist_ok=True)
    (root / "include").mkdir(parents=True, exist_ok=True)
    (root / "include" / "kern.h").write_text(_PROJ_HEADER)
    (root / "src" / "kern.c").write_text(_PROJ_KERN)
    (root / "src" / "main.c").write_text(_PROJ_MAIN)
    problems: List[str] = []
    proj = project_mod.Project.discover(root)
    if proj.units != ("src/kern.c", "src/main.c") or proj.include_dirs != ("include",):
        return Result(name, "fail", f"discovery found units {proj.units}, includes {proj.include_dirs}")
    kern, main_c = root / "src" / "kern.c", root / "src" / "main.c"

    def loops(dp: Path) -> Dict[Tuple[str, int], bool]:
        fm = {fid: p.name for fid, p in project_mod.load_file_mapping(dp).items()}
        pats = json.loads((dp / "explorer" / "patterns.json").read_text())["patterns"]
        out: Dict[Tuple[str, int], bool] = {}
        for p in pats.get("do_all", []) + pats.get("reduction", []):
            fid, line = (int(x) for x in str(p["start_line"]).split(":"))
            out[(fm.get(fid, "?"), line)] = str(p.get("applicable_pattern")) == "True"
        return out

    # 1. DiscoPoP's own way, unit by unit — recorded, because it is WHY the unity unit exists.
    per_unit = work / "proj_per_unit"
    shutil.copytree(root, per_unit)
    ok, err = _run([_venv_bin("discopop_cc"), "src/kern.c", "src/main.c", "-Iinclude", "-o", "a.out"], per_unit)
    note = "per-unit profile not available"
    if ok and _run(["./a.out"], per_unit)[0] and _run([_venv_bin("discopop_explorer")], per_unit / ".discopop")[0]:
        wrong = sorted(l for (f, l), okp in loops(per_unit / ".discopop").items() if f == "kern.c" and okp and l in (8, 14))
        note = (f"DiscoPoP unit by unit calls the recurrence(s) at kern.c:{wrong} Do-All" if wrong
                else "DiscoPoP unit by unit no longer mis-reports the recurrences (unity unit may be unnecessary)")

    project_mod.activate(proj)
    try:
        project_mod.set_focus(kern)
        dp = root / ".discopop"
        if not _reprofil(str(kern), dp, None):
            return Result(name, "fail", "the unity profile failed")
        if proj.unity_path().exists():
            problems.append("the generated unity unit was left in the project")
        found = loops(dp)
        if not found.get(("kern.c", 7)):
            problems.append(f"the independent loop kern.c:7 is not reported parallel ({found})")
        # The clauses come from the explorer's AST-based classification, which matches
        # declarations to files by path: compiled by a relative name the unity unit's
        # includes are recorded as "./src/kern.c" and every loop lost its clauses.
        pats = json.loads((dp / "explorer" / "patterns.json").read_text())["patterns"]
        kern_id = next(i for i, pth in project_mod.load_file_mapping(dp).items() if pth.name == "kern.c")
        outer = [p for p in pats.get("do_all", []) if str(p.get("start_line")) == f"{kern_id}:7"]
        if not outer or "t" not in (outer[0].get("private") or []):
            problems.append(f"the Do-All on kern.c:7 lost its clauses in the unity profile: "
                            f"{outer[0] if outer else 'no pattern'}")
        bad = sorted(l for (f, l), okp in found.items() if f == "kern.c" and okp and l in (8, 14))
        if bad:
            problems.append(f"recurrence(s) at kern.c:{bad} reported Do-All through the unity unit")

        # 2. Every region is attributed to the file it lives in.
        cands = build_candidates(dp, str(kern), 0.0, min_workload=0.0)
        by_file = {Path(c.source_file).name for c in cands}
        if by_file != {"kern.c", "main.c"}:
            problems.append(f"regions attributed to {sorted(by_file)}")
        if any(Path(c.source_file).name == "kern.c" and c.region.start_line == 3 for c in cands):
            problems.append("main()'s region (main.c:3) was attributed to kern.c")

        # 3. The gate builds the REAL program and judges a change in the unit without main().
        ref, _t, refs = capture_reference(str(kern), None)
        if ref is None:
            return Result(name, "fail", "the multi-file program could not be built for the reference")
        text = kern.read_text()
        good = make_diff(text, text.replace("  for (i = 0; i < n; i++)\n", "  #pragma omp parallel for private(t)\n  for (i = 0; i < n; i++)\n", 1), str(kern))
        racy = make_diff(text, text.replace("  for (i = 1; i < n; i++)\n", "  #pragma omp parallel for\n  for (i = 1; i < n; i++)\n", 1), str(kern))
        r_good = validate(good, str(kern), reference_output=ref, reference_outputs=refs, mode="safety")
        r_racy = validate(racy, str(kern), reference_output=ref, reference_outputs=refs, mode="safety")
        if not r_good.passed:
            problems.append(f"a correct pragma in kern.c failed at {r_good.stage}: {r_good.diagnostic[:80]}")
        if r_racy.passed:
            problems.append("a pragma on the recurrence in kern.c passed the gate")
        if kern.read_text() != text:
            problems.append("the gate modified the project's real file")

        # 3b. The project's OWN build command, both ways flags can reach it.
        from ..gate.patching import run_build
        from ..gate.toolchain import _find_clangpp, _macos_sysroot_flag, link_flags_for
        cand = work / "kern_candidate.c"
        cand.write_text(text.replace("* 0.5 + 1.0", "* 0.5 + 2.0"))
        for label, cmd in (("placeholders", "{cc} {flags} src/kern.c src/main.c -Iinclude -o {out}"),
                           ("environment", 'sh -c "$CC $CFLAGS src/kern.c src/main.c -Iinclude -o a.out"')):
            custom = project_mod.Project.discover(root, build_cmd=cmd, binary="a.out")
            project_mod.activate(custom)
            project_mod.set_focus(kern)
            out_bin = work / f"bin_{label}"
            r = run_build(cand, _find_clangpp() or "clang++", out_bin,
                          ["-O2"] + link_flags_for(cand) + _macos_sysroot_flag(), work)
            got = subprocess.run([str(out_bin)], capture_output=True, text=True).stdout.strip() if out_bin.exists() else ""
            if r.returncode != 0 or not got.startswith("2383.99"):
                problems.append(f"--build-cmd via {label}: rc {r.returncode}, output {got!r} "
                                f"(the candidate should double the constant)")
        if kern.read_text() != text or any(p.name.startswith("_dp_proj") for p in work.iterdir()):
            problems.append("a build-cmd build touched the real tree or left its staging behind")
        project_mod.activate(proj)
        project_mod.set_focus(kern)

        # 4. A fast refresh after an edit to kern.c moves kern.c's lines and nobody else's.
        from ..evidence.deps import _load_instruction_lines
        from ..profiling import _reprofil_fast

        def deps_within(file_name: str) -> int:
            """Observed dependence rows whose sink AND sources all sit in `file_name`."""
            fid = next(i for i, pth in project_mod.load_file_mapping(dp).items() if pth.name == file_name)
            where = _load_instruction_lines(dp / "profiler")
            n = 0
            for row in (dp / "profiler" / "dynamic_dependencies.txt").read_text().splitlines():
                f = row.split()
                if len(f) < 4 or f[1] != "NOM":
                    continue
                ends = [f[0]] + [t.split("|")[0] for t in f[3::2] if "|" in t]
                files = {where.get(e.split("@")[0], (0, 0))[0] for e in ends if e not in ("*", "0@0")}
                n += files == {fid}
            return n

        main_deps_before = deps_within("main.c")
        new_text = text.replace("void kernel(int n)\n", "/* added */\n/* lines */\nvoid kernel(int n)\n", 1)
        kern.write_text(new_text)
        out_dir = work / "proj_out"
        out_dir.mkdir(exist_ok=True)
        ok_f, note_f = _reprofil_fast(str(kern), dp, text, new_text, out_dir)
        kern.write_text(text)
        if not ok_f:
            problems.append(f"fast refresh failed on the project: {note_f}")
        else:
            moved = loops(dp)
            if not moved.get(("kern.c", 9)) or ("kern.c", 7) in moved:
                problems.append(f"kern.c's loop did not move 7 -> 9 ({sorted(moved)})")
            if ("main.c", 5) not in moved:
                problems.append(f"main.c's loop at line 5 moved although main.c was not edited ({sorted(moved)})")
            main_deps_after = deps_within("main.c")
            if main_deps_before == 0 or main_deps_after != main_deps_before:
                problems.append(f"main.c was not edited, yet {main_deps_before} of its observed "
                                f"dependences became {main_deps_after} after the refresh")
    finally:
        project_mod.activate(None)
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", f"{note}; through the unity unit they are blocked (clauses intact) and regions "
                                f"keep their real file and line; the gate built both units, passed a correct "
                                f"pragma in the unit without main() and caught a racy one; --build-cmd works "
                                f"with placeholders and with CC/CFLAGS; a refresh moved only the edited file")


_NEST_SRC = (
    "#include <stdio.h>\n#define R 300\n#define T 40\nstatic double a[R][T];\n"
    "int main(void) {\n  int i, t;\n"
    "  for (i = 0; i < R; i++) a[i][0] = 1.0 + (i % 17) * 0.25;\n"
    "  for (i = 0; i < R; i++)\n    for (t = 1; t < T; t++)\n"
    "      a[i][t] = a[i][t-1] * 0.5 + 1.0;\n"
    "  double s = 0.0;\n  for (i = 0; i < R; i++) s += a[i][T-1];\n"
    "  printf(\"%.10f\\n\", s);\n  return 0;\n}\n")


def check_dependence_standing(work: Path) -> Result:
    """The profile may judge a pragma only on code it actually profiled.

    Two defects, both found on real benchmarks (review F6).  The stage judged a
    REWRITE by the original loop's observed dependences — so the correct
    Floyd-Warshall parallelisation failed, removing that dependence being the
    whole point of the rewrite.  And it matched blockers by OVERLAP with the
    region, so an inner recurrence failed DiscoPoP's own correct pragma on the
    independent loop around it.  The blocker file is written by hand here, so
    the check does not depend on which output the explorer happens to draw.
    """
    import json
    from ..gate.dependences import annotated_loop_lines, dependence_evidence
    name = "dep standing"
    d = work / "dep_standing"
    (d / ".discopop" / "explorer").mkdir(parents=True, exist_ok=True)
    src = d / "nest.c"
    src.write_text(_NEST_SRC)
    lines = _NEST_SRC.splitlines()
    outer = next(i for i, l in enumerate(lines, 1) if l.startswith("  for (i = 0; i < R; i++)") and "a[i][0]" not in l and "s +=" not in l)
    inner = outer + 1
    (d / ".discopop" / "explorer" / "doall_prevented.json").write_text(json.dumps([{
        "loop_file": 1, "loop_start": inner, "loop_end": inner, "dep_type": "DepType.RAW",
        "source_line": "None", "sink_line": "None", "var_name": "GEPRESULT_a",
        "origin": "DepOrigin.DYNAMIC_ANALYSIS"}]))
    dp = str(d / ".discopop")
    text = src.read_text()
    o_head, i_head = lines[outer - 1] + "\n", lines[inner - 1] + "\n"

    ann_outer = make_diff(text, text.replace(o_head + i_head, "  #pragma omp parallel for private(t)\n" + o_head + i_head, 1), str(src))
    ann_inner = make_diff(text, text.replace(o_head + i_head, o_head + "    #pragma omp parallel for\n" + i_head, 1), str(src))
    rewrite = make_diff(text, text.replace(i_head, "    for (t = 1; t < T; t += 1)\n", 1).replace(
        o_head, "  #pragma omp parallel for private(t)\n" + o_head, 1), str(src))

    problems = []
    if annotated_loop_lines(ann_outer) != [outer]:
        problems.append(f"outer annotation located at {annotated_loop_lines(ann_outer)}, want [{outer}]")
    if annotated_loop_lines(rewrite) is not None:
        problems.append("a diff that changes code was classified as a pure annotation")
    v_outer = dependence_evidence(dp, 1, outer, inner + 1, loop_lines=annotated_loop_lines(ann_outer)).verdict
    v_inner = dependence_evidence(dp, 1, outer, inner + 1, loop_lines=annotated_loop_lines(ann_inner)).verdict
    if v_outer == "contradicted":
        problems.append("an INNER loop's blocker failed a pragma on the independent outer loop")
    if v_inner != "contradicted":
        problems.append(f"a pragma on the loop with the OBSERVED dependence was not contradicted ({v_inner})")
    # End to end: the rewrite must reach the evidence as "rewritten-code", never fail here.
    from ..gate import capture_reference
    from ..gate.validate import validate
    ref, _t, refs = capture_reference(str(src), None)
    res = validate(rewrite, str(src), reference_output=ref, reference_outputs=refs,
                   discopop_dir=dp, dep_region=(1, outer, inner + 1), mode="safety")
    if res.stage == "dependences":
        problems.append("a rewrite was failed by the original code's dependences")
    elif res.evidence.get("dependences") != "rewritten-code":
        problems.append(f"rewrite evidence reads {res.evidence.get('dependences')!r}")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", "rewrite not judged by the old profile; outer Do-All survives an inner "
                                "blocker; the blocked loop itself is still contradicted")


def check_schedule_runtime(work: Path) -> Result:
    """The schedule matrix must actually vary the schedule (review F8).

    OMP_SCHEDULE is obeyed only by loops declaring `schedule(runtime)`, so the
    stress build has to add it to every worksharing loop that names no schedule.
    """
    from ..gate.schedules import with_runtime_schedule
    name = "schedule runtime"
    cases = [
        ("#pragma omp parallel for\nfor(;;);", 1),
        ("  #pragma omp parallel for private(j) reduction(+:s)\n", 1),
        ("#pragma omp for\n", 1),
        ("#pragma omp parallel for schedule(static)\n", 0),      # named: left alone
        ("#pragma omp parallel for schedule (dynamic, 4)\n", 0),
        ("#pragma omp parallel\n{\n", 0),                         # not a loop construct
        ("#pragma omp simd\n", 0),
        ("#pragma omp task\n", 0),
        ("#pragma omp parallel for \\\n    private(j)\n", 1),     # continuation line
        ("// #pragma omp parallel for is mentioned in a comment\n", 0),
    ]
    bad = []
    for text, want in cases:
        out, n = with_runtime_schedule(text)
        if n != want or (want and "schedule(runtime)" not in out) or (not want and out != text):
            bad.append(f"{text.splitlines()[0][:40]!r}: changed {n}, want {want}")
    cont, _ = with_runtime_schedule("#pragma omp parallel for \\\n    private(j)\n")
    if not cont.splitlines()[1].rstrip().endswith("schedule(runtime)"):
        bad.append("a continued pragma did not get the clause on its LAST line")
    if bad:
        return Result(name, "fail", "; ".join(bad))
    return Result(name, "pass", f"{len(cases)} pragma shapes: clause added only to unscheduled loop constructs")


_REDUCE_SRC = (
    "#include <stdio.h>\n#include <stdlib.h>\n#define N 400000\nstatic double a[N], b[N];\n"
    "int main(int argc, char** argv) {\n  int i; double acc = 0.0;\n"
    "  for (i = 0; i < N; i++) { a[i] = (i % 613) * 0.125; b[i] = (i % 149) * 0.75; }\n"
    "  if (argc > 1) { unsigned long long st = strtoull(argv[1], 0, 10) * 2654435761ULL + 1;\n"
    "    for (i = 0; i < N; i++) { st = st * 6364136223846793005ULL + 1442695040888963407ULL;\n"
    "      a[i] += (double)(st >> 11) / 9007199254740992.0; } }\n"
    "  for (i = 0; i < N; i++)\n    acc += a[i] * b[i];\n"
    "  printf(\"%.17g\\n\", acc);\n  return 0;\n}\n")


def check_noise_floor_inputs(work: Path) -> Result:
    """The floor is measured on every input it is applied to, and Settle uses it.

    Review F10: the default input of this program is exactly representable, so it
    rounds nowhere and measures a floor of 0, while the seeded input does round —
    and a correct `reduction` was then rejected on it byte-for-byte.  Review F9:
    Settle re-judged the finished file with no floor at all.
    """
    from ..gate import capture_reference, numerical_noise_floor
    from ..gate.validate import validate
    name = "noise floor inputs"
    d = work / "floor_inputs"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "reduce.c"
    src.write_text(_REDUCE_SRC)
    f_default = numerical_noise_floor(str(src), None).value
    f_all = numerical_noise_floor(str(src), None, extra_inputs=[["7"]]).value
    if f_default != 0.0:
        return Result(name, "skip", f"default input is not rounding-free here ({f_default:.1e})")
    if f_all <= 0.0:
        return Result(name, "fail", "the floor ignores the extra input (still 0)")
    text = src.read_text()
    loop = "  for (i = 0; i < N; i++)\n    acc += a[i] * b[i];"
    diff = make_diff(text, text.replace(loop, "  #pragma omp parallel for reduction(+:acc)\n" + loop, 1), str(src))
    ref, _t, refs = capture_reference(str(src), None, extra_inputs=[["7"]])
    with_floor = validate(diff, str(src), reference_output=ref, reference_outputs=refs,
                          noise_floor=f_all, mode="safety")
    if not with_floor.passed:
        return Result(name, "fail", f"a correct reduction failed at '{with_floor.stage}' with the floor in effect")

    # Settle must judge the finished file with that same floor.
    from types import SimpleNamespace
    from ..phases.settle import _check_final_source
    final = text.replace(loop, "  #pragma omp parallel for reduction(+:acc)\n" + loop, 1)
    src.write_text(final)
    args = SimpleNamespace(source_file=str(src), noise_floor=f_all, schedule_stress=True,
                           stress_threads=(1, 2, 4), require_speedup=False, timing_cflags=())
    ok, why = _check_final_source(args, text, ref, refs, None, None)   # type: ignore[arg-type]
    src.write_text(text)
    if not ok:
        return Result(name, "fail", f"Settle rejected what the gate accepted: {why[:120]}")
    return Result(name, "pass", f"floor 0 on the default input, {f_all:.1e} with the seeded one; "
                                f"a correct reduction passes the gate and Settle")


_SETTLE_SPEED_SRC = r"""
#include <stdio.h>
static const int N = 120000;
static const int WORK = 400;
static double a[N], out[N];
int main(void) {
    for (int i = 0; i < N; i++) a[i] = 1.0 + (i % 97) * 0.01;
    for (int i = 0; i < N; i++) {
        double x = a[i];
        for (int k = 0; k < WORK; k++) x = x * 0.9999993 + 1e-7 * (k & 7);
        out[i] = x;
    }
    long long chk = 0;
    for (int i = 0; i < N; i++) chk += (long long)(out[i] * 1000.0);
    printf("checksum %lld\n", chk);
    return 0;
}
"""


def check_settle_paired(work: Path) -> Result:
    """Settle's speed verdict is PAIRED: the machine's state when the run began is not a
    baseline.  (Fix 89)

    Settle used to time the finished program alone and compare it with the reference time
    captured at the start of the run — minutes earlier, from a non-OpenMP build — and call
    the program slower when the two differed by more than the noise allowance.  On the
    campaign's shared host that threw away 15 of 90 class-R TSVC trials whose pragmas
    Phase B had just measured, interleaved, at 1.02–1.84×: Settle reported them 1.1–8×
    slower than a number taken before the model was even called.

    The check hands Settle a reference time that is absurdly small — as if the host had
    become eight times slower since the run began — with a finished file that really is
    faster (a clean do-all under `parallel for`): it must pass.  A finished file that really
    is slower (the same loop with its work doubled) must still be rejected.
    """
    name = "settle paired speed"
    from types import SimpleNamespace
    from ..gate import capture_reference
    from ..phases.settle import _check_final_source
    d = work / "settle_paired"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "settle_speed.cpp"
    src.write_text(_SETTLE_SPEED_SRC)
    text = _SETTLE_SPEED_SRC
    ref, t_ref, refs = capture_reference(str(src), None)
    if ref is None or t_ref is None:
        return Result(name, "skip", "could not capture the reference")
    loop = "    for (int i = 0; i < N; i++) {\n        double x = a[i];"
    assert text.count(loop) == 1
    faster = text.replace(loop, "    #pragma omp parallel for\n" + loop, 1)
    slower = text.replace("static const int WORK = 400;", "static const int WORK = 800;", 1)
    args = SimpleNamespace(source_file=str(src), noise_floor=0.0, schedule_stress=True,
                           stress_threads=(1, 2, 4), require_speedup=True, timing_cflags=())
    stale = t_ref / 8.0                      # the reference, "taken on a machine 8× faster"
    src.write_text(faster)
    ok_f, why_f = _check_final_source(args, text, ref, refs, None, stale, 0.97)   # type: ignore[arg-type]
    src.write_text(slower)
    ok_s, why_s = _check_final_source(args, text, ref, refs, None, t_ref, 0.97)   # type: ignore[arg-type]
    src.write_text(text)
    if not ok_f:
        return Result(name, "fail", f"a faster finished file was rejected against a stale reference: {why_f[:120]}")
    if ok_s:
        return Result(name, "fail", f"a finished file with twice the work was kept: {why_s[:120]}")
    return Result(name, "pass", f"faster file kept against a reference 8× too small ({why_f[:60]}); "
                                f"slower file rejected ({why_s[:60]})")


def check_phase_b_joint(work: Path) -> Result:
    """D33 — pragmas that do not pay ALONE are judged as a set, and the set lands as one unit.

    E1 (`e1b_marginal_replay`): when a rewrite splits a loop into two, each of DiscoPoP's two
    pragmas measured alone lost (0.6–1.0×) while both together were 2.5–4× the rewrite, and
    Phase B — which measures one pragma at a time — dropped both, in 7 of 18 trials. Speed is
    stood in (scripted by how many pragmas each side carries) and so is the safety gate: the
    check is about the decision, not about a machine. Four cases: the pair pays → both kept
    as ONE change-log entry carrying both regions; the pair does not pay → the file is left as
    it was; a member that adds nothing → left out by the backward elimination; a single
    deferred pragma → dropped exactly as before D33.
    """
    name = "phase-b joint"
    from types import SimpleNamespace
    from ..llm import make_diff
    from ..phases import phase_b as pb
    from ..types import ValidationResult
    d = work / "phase_b_joint"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "split.c"
    text = ("void f(int n, double *a, double *b, double *t) {\n"
            "  for (int i = 0; i < n - 1; i++) {\n    t[i] = a[i + 1] + b[i];\n  }\n"
            "  for (int i = 0; i < n - 1; i++) {\n    a[i] = t[i];\n  }\n}\n")
    heads = ["  for (int i = 0; i < n - 1; i++) {\n    t[i]", "  for (int i = 0; i < n - 1; i++) {\n    a[i]"]
    dp = d / ".discopop"
    for pid, h in ((1, heads[0]), (2, heads[1])):
        pdir = dp / "patch_generator" / str(pid)
        pdir.mkdir(parents=True, exist_ok=True)
        (pdir / "p.patch").write_text(make_diff(text, text.replace(h, "  #pragma omp parallel for\n" + h, 1),
                                                str(src)))

    def deferred(which: List[int]) -> List[Dict[str, Any]]:
        spans = {1: (2, 4), 2: (5, 7)}
        return [{"cand": SimpleNamespace(source_file=str(src), region=SimpleNamespace(
                    file_id=1, start_line=spans[p][0], end_line=spans[p][1], region_id=f"1:{p}",
                    region_type="loop", name=f"loop{p}"), workload_estimate=1000.0),
                 "ptype": "do_all", "pid": p, "pragma": "#pragma omp parallel for",
                 "lines": f"{spans[p][0]}–{spans[p][1]}",
                 "res": ValidationResult(passed=True, stage="accepted"), "alone": 0.8} for p in which]

    def run(which: List[int], pair: float, without_second: float) -> Tuple[str, List[Any], List[Any]]:
        def fake_measure(before: str, after: str, *a: Any, **k: Any) -> Tuple[bool, float, str]:
            nb, na = before.count("#pragma omp"), after.count("#pragma omp")
            if na - nb == 2:
                return True, pair, ""
            if na - nb == 1:
                return True, 0.8, ""
            if na < nb:                      # a member removed from the set
                second_gone = "  #pragma omp parallel for\n" + heads[1] not in after
                return True, (without_second if second_gone else 0.4), ""
            return True, 1.0, ""

        def fake_gate(*a: Any, **k: Any) -> Tuple[ValidationResult, bool, bool]:
            return ValidationResult(passed=True, stage="accepted"), False, False

        src.write_text(text)
        saved = (getattr(pb, "measure_marginal"), getattr(pb, "_validate_cached"))
        setattr(pb, "measure_marginal", fake_measure)
        setattr(pb, "_validate_cached", fake_gate)
        change_log: List[Any] = []
        args = SimpleNamespace(source_file=str(src), project=None, timing_cflags=(), apply_patches=True,
                               dry_run=False)
        try:
            kept = getattr(pb, "_judge_jointly")(args, dp, d / "out", deferred(which), [], 0.99,
                                                 None, None, None, None, {}, change_log, None)
        finally:
            setattr(pb, "measure_marginal", saved[0])
            setattr(pb, "_validate_cached", saved[1])
        return src.read_text(), kept, change_log

    (d / "out").mkdir(exist_ok=True)
    body, kept, log = run([1, 2], 2.0, 0.4)
    if body.count("#pragma omp") != 2 or len(kept) != 2 or len(log) != 1 \
            or len(log[0].get("fingerprints", [])) != 2 or log[0].get("region_ids") != ["1:1", "1:2"]:
        return Result(name, "fail", f"a pair that pays together: {body.count('#pragma omp')} pragma(s) in the "
                                    f"file, {len(kept)} record(s), {len(log)} change-log entr(y/ies) — want 2, 2, 1")
    body, kept, log = run([1, 2], 0.9, 0.4)
    if body != text or kept or log:
        return Result(name, "fail", "a pair that does not pay together changed the file")
    body, kept, log = run([1, 2], 2.0, 1.0)
    if body.count("#pragma omp") != 1 or len(kept) != 1 or log[0].get("region_ids") != ["1:1"]:
        return Result(name, "fail", "a member that adds nothing was not left out of the set")
    body, kept, log = run([1], 2.0, 0.4)
    if body != text or kept or log:
        return Result(name, "fail", "a single deferred pragma was kept (it must be dropped as before D33)")
    src.write_text(text)
    return Result(name, "pass", "pair paying together kept as one unit; pair not paying left out; dead-weight "
                                "member eliminated; a lone deferred pragma dropped as before")


def check_dp_floor(work: Path) -> Result:
    """D32 — the agent's program may not end below DiscoPoP's own.

    E1 class A: on `vpvtv` the finished program ran at 2.37× where DiscoPoP alone reached
    4.08× (worse); on `s000` the rewrite ended slower than the original, Settle reverted
    everything and DiscoPoP's own 4.03× pragma went with it (lost). Phase B, Settle and the
    timing are stood in: the check is about the floor's bookkeeping and its decision. The
    floor is built and the ORIGINAL put back for the agent; with nothing kept by DiscoPoP
    there is no floor; a slower agent program is replaced by the floor (its records too); a
    faster one is kept; an identical one is not even timed; and the `s000` shape — the agent
    back at the original while DiscoPoP's pragma pays — ships DiscoPoP's program.
    """
    name = "dp floor"
    from types import SimpleNamespace
    from ..phases import floor as fl
    d = work / "dp_floor"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "k.c"
    orig = "void k(int n, double *a) {\n  for (int i = 0; i < n; i++) a[i] *= 2;\n}\n"
    dp_prog = orig.replace("  for", "  #pragma omp parallel for\n  for", 1)
    agent_prog = orig.replace("a[i] *= 2;", "a[i] = a[i] + a[i];", 1)
    key = str(src.resolve())
    args = SimpleNamespace(source_file=str(src), project=None, timing_cflags=())
    gate_cache: Dict[str, Any] = {"__speed_threshold__": 0.99}
    saved = {n: getattr(fl, n) for n in ("_phase_b", "_settle", "measure_marginal")}
    timed: List[Tuple[str, str]] = []

    def fake_phase_b(*a: Any, **k: Any) -> List[Dict[str, Any]]:
        change_log = a[8]
        if keep_dp:
            src.write_text(dp_prog)
            change_log.append({"kind": "pragma", "region_id": "1:2", "diff": "", "fingerprint": "f"})
            return [{"phase": "B", "region_id": "1:2", "pragma": "#pragma omp parallel for"}]
        return []

    def fake_settle(originals: Any, log: Any, *a: Any, **k: Any) -> Tuple[List[Any], List[Any]]:
        return list(log), []

    def fake_measure(before: str, after: str, *a: Any, **k: Any) -> Tuple[bool, float, str]:
        timed.append((before, after))
        return True, ratio, ""

    try:
        setattr(fl, "_phase_b", fake_phase_b)
        setattr(fl, "_settle", fake_settle)
        setattr(fl, "measure_marginal", fake_measure)
        keep_dp = True
        src.write_text(orig)
        texts, acc = fl.build_floor(args, d, d, {key: orig}, "", None, None, None,  # type: ignore[arg-type]
                                    gate_cache, None)
        if texts is None or texts[key] != dp_prog or src.read_text() != orig or len(acc) != 1:
            return Result(name, "fail", "the floor was not captured, or the original was not put back")
        keep_dp = False
        src.write_text(orig)
        none_texts, _ = fl.build_floor(args, d, d, {key: orig}, "", None, None, None,  # type: ignore[arg-type]
                                       gate_cache, None)
        if none_texts is not None:
            return Result(name, "fail", "DiscoPoP kept nothing, yet a floor was set")
        floor_acc = [{"phase": "B", "region_id": "1:2"}]
        agent_acc = [{"phase": "A", "region_id": "1:1", "tier": 2}]
        cases = [("agent slower than the floor", agent_prog, 0.6, dp_prog, floor_acc),
                 ("agent faster than the floor", agent_prog, 1.3, agent_prog, agent_acc),
                 ("agent program IS the floor", dp_prog, 0.1, dp_prog, agent_acc),
                 ("s000: agent back at the original", orig, 0.25, dp_prog, floor_acc)]
        for label, final, ratio, want_disk, want_acc in cases:
            src.write_text(final)
            timed.clear()
            got = fl.apply_floor(args, {key: orig}, {key: dp_prog}, floor_acc, agent_acc,  # type: ignore[arg-type]
                                 None, gate_cache, d)
            if src.read_text() != want_disk or got != want_acc:
                return Result(name, "fail", f"{label}: wrong program or records shipped")
            if label == "agent program IS the floor" and timed:
                return Result(name, "fail", "an agent program identical to the floor was timed")
    finally:
        for n, f in saved.items():
            setattr(fl, n, f)
        src.write_text(orig)
    return Result(name, "pass", "floor built and original restored; none when DiscoPoP keeps nothing; slower "
                                "agent program replaced by the floor, faster kept, identical not timed, s000 "
                                "shape ships DiscoPoP's")


_MULTI_BACKEDGE_SRC = r"""
#include <stdio.h>
#include <stdlib.h>
#define N 60
static int m[N * N];
static double b[N * N];
int main(void) {
  int i, j;
  for (i = 0; i < N * N; i++) { m[i] = (i * 7919) % 13; b[i] = 0.0; }
  /* a loop with several paths back to its header: two `continue`s and the plain end */
  for (i = 0; i < N * N; i++) {
    if (i % 3 == 0) { b[i] = m[i] * 2.0; continue; }
    if (i % 5 == 0) { b[i] = m[i] + 1.0; continue; }
    b[i] = m[i] - 1.0;
  }
  /* Rodinia nw's traceback walk: a short-circuit condition in the header (a branch at the
     loop's entry), no increment, and three `continue`s — four back edges to one header */
  long walked = 0;
  for (i = N - 1, j = N - 1; i >= 0 && j >= 0;) {
    int here = m[i * N + j];
    if (i == 0 && j == 0) break;
    walked += here;
    if (i > 0 && j > 0 && here % 3 == 0) { i--; j--; continue; }
    else if (j > 0 && here % 3 == 1) { j--; continue; }
    else if (i > 0) { i--; continue; }
    else { break; }
  }
  double s = 0.0;
  for (i = 0; i < N * N; i++) s += b[i];
  printf("%.3f %ld\n", s, walked);
  return 0;
}
"""


def check_explorer_multi_backedge(work: Path) -> Result:
    """DiscoPoP's explorer must analyse a loop with several back edges (Fix 80).

    The task-graph builder broke ONE cycle per loop header and re-wired the other
    back edges — `continue` statements, the arms of a branch — to the new StartLoop
    marker, which made a second cycle through the same header, a second set of
    markers chained onto the first and 'Invalid iteration structure' in
    __assign_loop_contexts.  Rodinia nw's traceback loop (three `continue`s) failed
    that way on every attempt, so no trial of nw could have existed.  Here: one
    bounded loop with two `continue`s and one unbounded loop that leaves only by
    break/continue; the explorer must finish and report the bounded loop's
    independent iterations as a Do-All.
    """
    name = "explorer multi-backedge"
    d = work / "multi_backedge"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    (d / "walk.c").write_text(_MULTI_BACKEDGE_SRC)
    ok, err = _profile(d, "walk.c", hotspots=False, c_as_c=True)
    if not ok:
        return Result(name, "fail", err[:200])
    patterns = json.loads((d / ".discopop" / "explorer" / "patterns.json").read_text())["patterns"]
    lines = sorted(int(str(p.get("start_line", "0:0")).split(":")[1]) for p in patterns.get("do_all", []))
    src_lines = _MULTI_BACKEDGE_SRC.splitlines()
    want = next(i for i, l in enumerate(src_lines, 1) if "for (i = 0; i < N * N; i++) {" in l)
    if want not in lines:
        return Result(name, "fail", f"the loop with two `continue`s (line {want}) is not a Do-All; do_all at {lines}")
    return Result(name, "pass", f"explorer finished; Do-All at lines {lines} includes the multi-back-edge loop ({want})")


_ELSE_LOOP_SRC = r"""
#include <stdio.h>
#include <stdlib.h>
#define N 40
static double w[N][N], r[N];
static void fill(int seeded) {
  int i, j;
  for (i = 0; i < N; i++) r[i] = 0.0;
  if (seeded) {
    for (i = 0; i < N; i++)
      for (j = 0; j < N; j++)
        w[i][j] = (double)((i * 31 + j * 17) % 10);
  } else {
    for (i = 0; i < N; i++)
      for (j = 0; j < N; j++)
        w[i][j] = (double)((i + j) % 10);
  }
  for (j = 0; j < N; j++) r[j] = w[0][j];
}
int main(int argc, char** argv) {
  fill(argc > 1);
  double s = 0.0;
  for (int j = 0; j < N; j++) s += r[j];
  printf("%.1f\n", s);
  return 0;
}
"""


def check_profiler_else_loop(work: Path) -> Result:
    """Every loop of a function gets loop markers — also one that ends an `else` block.

    DiscoPoP bug B3 (docs/DISCOPOP_BUG_REPORTS.md): clang gives the branch that ends an
    `else` block no debug line, the profiler skipped a loop whose exit block had none, and
    the function's call-path loop states came out one position short.  The explorer then
    indexed past them (IndexError in TaskGraph.recursive_assignment, on SOME runs of one
    profile: pathfinder 40 of 60, NPB mg every attempt) and matched every later loop of the
    function to the wrong position.  Here `fill` has six loops, one nest ending an `else`:
    its loop states must have six positions, and the explorer must finish five times of five.
    """
    name = "profiler else-loop"
    d = work / "else_loop"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    (d / "fill.c").write_text(_ELSE_LOOP_SRC)
    ok, err = _profile(d, "fill.c", hotspots=False, c_as_c=True)
    mapping = d / ".discopop" / "profiler" / "stateID_to_callpath_mapping.txt"
    if not mapping.exists():
        return Result(name, "fail", f"no call-path mapping: {err[:160]}")
    widths = {len(m) for m in re.findall(r"\bfill_loopstate(\d+)", mapping.read_text())}
    if widths != {6}:
        return Result(name, "fail", f"`fill` has 6 loops, its loop states have {sorted(widths)} positions")
    crashes = 0 if ok else 1
    for _ in range(4):
        shutil.rmtree(d / ".discopop" / "explorer", ignore_errors=True)
        good, _e = _run([_venv_bin("discopop_explorer")], d / ".discopop")
        crashes += not good
    if crashes:
        return Result(name, "fail", f"the explorer crashed in {crashes} of 5 runs on one profile")
    return Result(name, "pass", "6 loops, 6 loop-state positions; explorer finished 5 of 5 runs")


_SIBLING_SRC = """\
void kernel(int n, double **A, double *x, double *y, double *tmp) {
  int i, j;
  for (i = 0; i < n; i++)
    {
      tmp[i] = 0;
      for (j = 0; j < n; j++)
        tmp[i] = tmp[i] + A[i][j] * x[j];
      for (j = 0; j < n; j++)
        y[j] = y[j] + A[i][j] * tmp[i];
    }
}
"""

_SIBLING_PATCH = """\
--- a/k.c
+++ b/k.c
@@ -6,6 +6,7 @@
       tmp[i] = 0;
       for (j = 0; j < n; j++)
         tmp[i] = tmp[i] + A[i][j] * x[j];
+      #pragma omp parallel for
       for (j = 0; j < n; j++)
         y[j] = y[j] + A[i][j] * tmp[i];
     }
"""


def check_pragma_sibling_loops(work: Path) -> Result:
    """Fix 84: a generated pragma must land on ITS loop when a sibling has the same header.

    PolyBench atax: two `for (j = 0; j < _PB_NY; j++)` two lines apart; DiscoPoP's patch
    for the second (a valid Do-All) was re-anchored onto the first (a recurrence on
    tmp[i]), raced under TSan and was dropped — the DiscoPoP-only baseline lost a pragma
    DiscoPoP had placed correctly.  Checked on the file as profiled and on the file after
    a pragma was inserted above (the shift that turns distance into a tie)."""
    name = "pragma on a sibling loop"
    from discopop_agent.pragmas.patch import derive_pragma_patch
    d = work / "sibling"
    d.mkdir(parents=True, exist_ok=True)
    shifted = _SIBLING_SRC.replace("  for (i = 0;", "  #pragma omp parallel for private(j)\n  for (i = 0;", 1)
    for label, text in (("as profiled", _SIBLING_SRC), ("after a pragma above", shifted)):
        f = d / "k.c"
        f.write_text(text)
        diff = derive_pragma_patch(_SIBLING_PATCH, str(f))
        if not diff:
            return Result(name, "fail", f"{label}: no patch derived")
        lines = diff.splitlines()
        at = next((k for k, l in enumerate(lines) if l.startswith("+") and "#pragma omp" in l), None)
        body = lines[at + 2].strip() if at is not None and at + 2 < len(lines) else ""
        if not body.startswith("y[j]"):
            return Result(name, "fail", f"{label}: the pragma for the y[j] loop was placed before `{body}`")
    return Result(name, "pass", "second of two identical loop headers annotated, as profiled and after a shift")


_ARB_SRC = """\
void kernel(int n, double **A, double **B) {
  int t, i, j;
  for (t = 0; t < 20; t++)
    {
      for (i = 1; i < n - 1; i++)
        for (j = 1; j < n - 1; j++)
          B[i][j] = 0.2 * (A[i][j] + A[i][j-1] + A[i][1+j] + A[1+i][j] + A[i-1][j]);
      for (i = 1; i < n-1; i++)
        for (j = 1; j < n-1; j++)
          A[i][j] = B[i][j];
    }
}
"""


def check_pragma_arbitration(work: Path) -> Result:
    """Fix 85: a model pragma on a loop DiscoPoP claimed is measured against DiscoPoP's.

    jacobi-2d: DiscoPoP claims the two stencil loops and Phase A defers them, but the
    enclosing FUNCTION goes to the model, which annotates them from inside its rewrite; Phase B
    then reports "no applicable pattern" and DiscoPoP's own pragma is never built. Checks the
    three outcomes without a model or a compiler: DiscoPoP's pragma wins when it measures
    faster, the model's stands inside the noise band, and a pragma identical to DiscoPoP's is
    not a collision at all."""
    name = "pragma arbitration (Fix 85)"
    from discopop_agent.pragmas import arbitrate_pragmas, pragma_collisions
    original = _ARB_SRC
    annotated = original.replace("      for (i = 1; i < n - 1; i++)",
                                 "      #pragma omp parallel for collapse(2) shared(A, B)\n      for (i = 1; i < n - 1; i++)", 1)
    inner = [{"line": 5, "kind": "do_all", "clauses": "private(j) shared(A, B)"}]
    found = pragma_collisions(original, annotated, inner)
    if len(found) != 1 or "collapse(2)" not in found[0]["model_pragma"]:
        return Result(name, "fail", f"the collision on the claimed loop was not found: {found}")

    def _gate_ok(_text: str) -> "tuple[bool, str]":
        return True, ""

    quiet = lambda *_a, **_k: None
    # DiscoPoP's is twice as fast -> its pragma must end up in the kept text
    text, rec = arbitrate_pragmas(annotated, original, inner, "k.c", _gate_ok,
                                  lambda b, a: (True, 0.5, ""), log=quiet)
    if rec[0]["winner"] != "discopop" or "private(j)" not in text or "collapse(2)" in text:
        return Result(name, "fail", f"DiscoPoP's faster pragma was not taken: {rec}")
    # within the noise band -> the model's stands
    text2, rec2 = arbitrate_pragmas(annotated, original, inner, "k.c", _gate_ok,
                                    lambda b, a: (True, 1.02, ""), log=quiet)
    if rec2[0]["winner"] != "model" or text2 != annotated:
        return Result(name, "fail", f"inside the noise band the model's pragma must stand: {rec2}")
    # DiscoPoP's alternative rejected by the gate -> the model's stands, and it is recorded
    _t3, rec3 = arbitrate_pragmas(annotated, original, inner, "k.c",
                                  lambda _t: (False, "race"), lambda b, a: (True, 0.5, ""), log=quiet)
    if rec3[0]["winner"] != "model" or rec3[0]["reason"] != "discopop_alternative_rejected":
        return Result(name, "fail", f"a rejected alternative must leave the model's pragma: {rec3}")
    # the same pragma written by either side is not a collision
    same = annotated.replace("#pragma omp parallel for collapse(2) shared(A, B)",
                             "#pragma omp parallel for private(j) shared(A, B)")
    if pragma_collisions(original, same, inner):
        return Result(name, "fail", "an identical pragma was reported as a collision")
    # a loop left to Phase B, as the prompt now asks, is not a collision either
    if pragma_collisions(original, original, inner):
        return Result(name, "fail", "an unannotated loop was reported as a collision")
    return Result(name, "pass", "collision found; faster side taken; noise band, gate rejection "
                                "and identical/absent pragmas handled")


def check_arg_dependencies(work: Path) -> Result:
    """Arguments that only work in combination must SAY so — error or resolve, never pretend.

    An argument silently ignored because of another is how an experiment measures something
    other than what its arm declares: `--llm-recon` does nothing without `--fast-refresh`,
    `--pragma-arbitration` does nothing without `--llm-pragmas`. Each pair is checked twice —
    asked for explicitly it must be refused, and left at its default it must resolve to what
    actually happens."""
    name = "argument dependencies"
    import subprocess

    def resolve(extra: List[str]) -> "Tuple[int, Dict[str, Any]]":
        r = subprocess.run([sys.executable, "-m", "discopop_agent", "--discopop-dir", ".",
                            "--source-file", "a.c", *extra, "--print-config"],
                           capture_output=True, text=True, cwd=str(_REPO), env=_env())
        try:
            return r.returncode, json.loads(r.stdout)
        except ValueError:
            return r.returncode, {}

    # asked for explicitly, with its prerequisite missing -> refused
    for extra, why in ((["--llm-recon", "--no-fast-refresh"], "--llm-recon without --fast-refresh"),
                       (["--pragma-arbitration", "--no-llm-pragmas"], "--pragma-arbitration without --llm-pragmas"),
                       (["--pragma-arbitration", "--llm-pragmas", "--no-require-speedup"],
                        "--pragma-arbitration without --require-speedup"),
                       (["--llm-recon", "--llm-deps", "--fast-refresh"], "--llm-recon together with --llm-deps"),
                       (["--llm-deps", "--no-fast-refresh"], "--llm-deps without --fast-refresh")):
        rc, _ = resolve(extra)
        if rc == 0:
            return Result(name, "fail", f"{why} was accepted; it should be refused")

    # left at its default, the resolved value must be what actually happens
    rc, cfg = resolve([])
    if rc != 0:
        return Result(name, "fail", "the default configuration was refused")
    if cfg.get("pragma_arbitration") is not False:
        return Result(name, "fail", "arbitration reports True under the default --no-llm-pragmas, "
                                    "where it can never fire")
    rc, cfg = resolve(["--llm-pragmas"])
    if cfg.get("pragma_arbitration") is not True:
        return Result(name, "fail", "arbitration reports False with --llm-pragmas and the speed check on")
    rc, cfg = resolve([])
    if cfg.get("llm_deps"):
        return Result(name, "fail", "llm_deps is on by default; it must be opt-in")
    return Result(name, "pass", "5 impossible combinations refused; arbitration resolves to "
                                "what actually happens (False without --llm-pragmas)")


def check_shipped_prompt(work: Path) -> Result:
    """D40 — with judge_as_shipped the agent's model reads what decides a trial, in the words the
    twins and the model alone read; without it every text is v2's.

    DiscoPoP writing the pragmas: step 4 says the build is timed against the program before the
    rewrite and that a loss reverts it with the ratio — no longer "the same build on one thread",
    which only Phase B's per-pragma check resembles.  The model writing them: the goal and the
    request name the original sequential program, and the timing step both comparisons the gate
    makes.  Every line that differs from v2 is a line about timing; with the speed check off
    nothing differs."""
    import dataclasses
    import difflib
    from .. import twin
    from ..llm.prompts import _system_prompt
    from ..llm.request import _build_direct_prompt
    from ..types import GateFacts
    name = "shipped prompt"
    ev = _fw_evidence()
    ws = Path("/tmp/ws/fw.c")
    problems: List[str] = []
    for speed in (True, False):
        v2 = GateFacts(require_speedup=speed, n_inputs=2, numeric=False, stress=True)
        v3 = dataclasses.replace(v2, judge_as_shipped=True)
        for pragmas in (False, True):
            includes: List[Optional[Set[str]]] = [None, set()]
            for include in includes:
                tag = (f"{'model' if pragmas else 'DiscoPoP'} pragmas/{'full' if include is None else 'none'}/"
                       f"{'speed' if speed else 'no speed'}")
                old, new = (_system_prompt("direct", pragmas, False, g, include) for g in (v2, v3))
                old_req, new_req = (_build_direct_prompt(ev, ws, include, pragmas, g) for g in (v2, v3))
                if not speed:
                    if (old, old_req) != (new, new_req):
                        problems.append(f"{tag}: the flag changes a text with the speed check off")
                    continue
                changed = [ln for ln in difflib.unified_diff((old + old_req).splitlines(),
                                                             (new + new_req).splitlines(), lineterm="", n=0)
                           if ln[:1] in "+-" and ln[:3] not in ("+++", "---")]
                off_topic = [ln for ln in changed if not re.search(
                    r"faster|timed|one thread|ratio|rewrite and has to|than both|reverted and you", ln)]
                if off_topic:
                    problems.append(f"{tag}: a line not about timing changed: {off_topic[0][:70]!r}")
                if not pragmas:
                    if "speed against the same build on one thread" in new:
                        problems.append(f"{tag}: still names the one-thread comparison")
                    if "as it stood before your" not in new or "reverted and you" not in new:
                        problems.append(f"{tag}: does not state the before-the-rewrite criterion and the revert")
                else:
                    if "measurably faster than the original sequential program" not in new \
                            or "against the original sequential program, and has to be faster" not in new:
                        problems.append(f"{tag}: the goal or the timing step does not name the original")
                    if new_req != twin._request(old_req):
                        problems.append(f"{tag}: the request is not the twin's words")
    if problems:
        return Result(name, "fail", "; ".join(problems[:3]))
    return Result(name, "pass", "v3 states the deciding comparison in the twins' words; only timing lines "
                  "differ from v2, and nothing differs with the speed check off")


_SHIP_SRC = """#include <stdlib.h>
void k(double *a, double *b, int n) {
  double *t = (double *)malloc(sizeof(double) * n);
  for (int i = 0; i < n; i++)
    t[i] = b[i] * 2.0;
  for (int j = 0; j < n; j++) {
    for (int m = 0; m < 4; m++)
      a[j] += t[j] + m;
  }
  free(t);
}
"""


def _ship_candidates(work: Path) -> "Tuple[Path, Path, List[Any]]":
    """A two-loop rewrite (a copy loop, then a nest) with DiscoPoP-style pragma patches on disk for
    the copy loop, the nest and the loop nested in it — the shape judge_as_shipped gets."""
    from types import SimpleNamespace
    from ..llm.diffs import make_diff
    d = work / "shipped"
    shutil.rmtree(d, ignore_errors=True)
    (d / ".discopop" / "patch_generator").mkdir(parents=True)
    src = d / "k.c"
    src.write_text(_SHIP_SRC)
    lines = _SHIP_SRC.splitlines()
    cands = []
    for pid, (head, end) in enumerate(((4, 5), (6, 9), (7, 8)), start=1):
        with_pragma = lines[:head - 1] + ["#pragma omp parallel for"] + lines[head - 1:]
        pdir = d / ".discopop" / "patch_generator" / str(pid)
        pdir.mkdir()
        (pdir / "1.patch").write_text(make_diff(_SHIP_SRC, "\n".join(with_pragma) + "\n", str(src)))
        cands.append(SimpleNamespace(
            region=SimpleNamespace(start_line=head, end_line=end, file_id=1, name="k", region_id=f"1:{pid}"),
            pattern={"pattern_id": pid, "applicable_pattern": True}, pattern_type="do_all",
            source_file=str(src), tier=1, workload_estimate=100.0))
    return d, src, cands


def check_shipped_judge(work: Path) -> Result:
    """D40 — judge_as_shipped: DiscoPoP's pragmas for the exposed loops through the safety gate,
    outermost first (a loop inside one judged safe gets none), staged together as TEXT, then the
    program with them timed against the program before the rewrite.  The real file is never
    written (its hash is taken before and after every case).

    Cases: safe and faster → ok, both outer loops staged, the nested one not; safe and slower →
    not_faster, naming what the rewrite added (a loop, an allocation); nothing safe → pattern_broken
    with the first failure; the SET unsafe where each alone passed → the outermost judged alone;
    a crash at the timing size → pattern_broken; a timing that fails otherwise → exposed (Phase B
    and Settle decide, as in v2)."""
    import hashlib
    from ..phases.verdicts import judge_as_shipped
    name = "shipped judge"
    d, src, cands = _ship_candidates(work)
    dp = d / ".discopop"
    before = _SHIP_SRC.replace("  for (int i = 0; i < n; i++)\n    t[i] = b[i] * 2.0;\n", "") \
                      .replace("  double *t = (double *)malloc(sizeof(double) * n);\n", "")
    digest = lambda: hashlib.sha256(src.read_bytes()).hexdigest()       # noqa: E731
    start = digest()
    problems: List[str] = []
    seen: Dict[str, Any] = {}

    def safe(diff: str, c: Any) -> "Tuple[bool, str]":
        seen.setdefault("validated", []).append(c.region.region_id if c is not None else "set")
        return True, ""

    def timing(ratio: float, ok: bool = True, diag: str = "") -> Callable[[str, str], "Tuple[bool, float, str]"]:
        def m(b: str, a: str) -> "Tuple[bool, float, str]":
            seen["staged"], seen["before"] = a, b
            return ok, ratio, diag
        return m
    r = judge_as_shipped(cands, before, dp, str(src), threshold=0.98, validate=safe, measure=timing(1.5))
    staged = seen.get("staged", "")
    if r.status != "ok" or r.speedup != 1.5:
        problems.append(f"safe and faster gave {r.status}")
    if staged.count("#pragma omp parallel for") != 2 or "#pragma omp parallel for\n    for (int m" in staged:
        problems.append(f"expected pragmas on the two outer loops only, staged {staged.count('#pragma omp')}")
    if "1:3" in seen.get("validated", []):
        problems.append("the loop nested in one judged safe was sent to the gate")
    if seen.get("before") != before:
        problems.append("not timed against the program before the rewrite")
    r = judge_as_shipped(cands, before, dp, str(src), threshold=0.98, validate=safe, measure=timing(0.5))
    if r.status != "not_faster" or "loop" not in r.diagnostic or "allocation" not in r.diagnostic:
        problems.append(f"safe and slower gave {r.status} / {r.diagnostic!r}")
    r = judge_as_shipped(cands, before, dp, str(src), threshold=0.98,
                         validate=lambda diff, c: (False, "tsan: race on t"), measure=timing(1.5))
    if r.status != "pattern_broken" or "race" not in r.diagnostic:
        problems.append(f"nothing safe gave {r.status}")
    seen.clear()
    r = judge_as_shipped(cands, before, dp, str(src), threshold=0.98,
                         validate=lambda diff, c: (c is not None, "" if c is not None else "tsan: together"),
                         measure=timing(1.5))
    if r.status != "ok" or seen.get("staged", "").count("#pragma omp parallel for") != 1:
        problems.append("an unsafe SET did not fall back to the outermost pragma alone")
    r = judge_as_shipped(cands, before, dp, str(src), threshold=0.98, validate=safe,
                         measure=timing(0.0, ok=False, diag="non-zero exit (-11): signal"))
    if r.status != "pattern_broken":
        problems.append(f"a crash at the timing size gave {r.status}")
    r = judge_as_shipped(cands, before, dp, str(src), threshold=0.98, validate=safe,
                         measure=timing(0.0, ok=False, diag="no valid timing samples"))
    if r.status != "exposed":
        problems.append(f"an unmeasurable timing gave {r.status}, not the v2 verdict")
    # D40.1 (a): a deeper level follows — the safety half only, nothing timed.
    seen.clear()
    r = judge_as_shipped(cands, before, dp, str(src), threshold=0.0, validate=safe, measure=None)
    if r.status != "safe_deferred" or "staged" in seen:
        problems.append(f"safety only (a deeper level follows) gave {r.status}, or timed it")
    r = judge_as_shipped(cands, before, dp, str(src), threshold=0.0,
                         validate=lambda diff, c: (False, "tsan: race on t"), measure=None)
    if r.status != "pattern_broken":
        problems.append(f"safety only, nothing safe, gave {r.status}")
    if digest() != start:
        problems.append("the real file was written")
    if problems:
        return Result(name, "fail", "; ".join(problems[:3]))
    return Result(name, "pass", "ok / not_faster (naming the added loop and allocation) / pattern_broken / "
                  "set fallback / crash / unmeasurable / safety only at a depth (safe_deferred, "
                  "pattern_broken); outermost-first; the real file never written")


def check_request_log(work: Path) -> Result:
    """D40 — every request the model is sent is kept: the system prompt once per distinct text,
    then one JSON line per call with the region, the attempt, what was sent and the reply.  Here a
    stand-in model answers in the wrong format, so the call is re-prompted twice: three lines."""
    import json as _json
    from ..llm import client
    name = "request log"
    d = work / "requests"
    shutil.rmtree(d, ignore_errors=True)
    saved = (getattr(client, "_complete"), getattr(client, "_make_client"))
    try:
        client.set_request_log(d)
        setattr(client, "_make_client", lambda *a, **k: None)
        setattr(client, "_complete", lambda *a, **k: "no diff here")
        out, _msgs, _reply = client.call_llm(_fw_evidence(), "m", provider="anthropic", edit_mode="diff")
    finally:
        setattr(client, "_complete", saved[0])
        setattr(client, "_make_client", saved[1])
        client.set_request_log(None)
    rows = [_json.loads(x) for x in (d / "requests.jsonl").read_text().splitlines()] \
        if (d / "requests.jsonl").exists() else []
    systems = list(d.glob("system_*.txt"))
    problems = []
    if out is not None:
        problems.append("a reply without a diff was accepted")
    if [r.get("attempt") for r in rows] != [0, 1, 2]:
        problems.append(f"expected attempts 0,1,2, logged {[r.get('attempt') for r in rows]}")
    if len(systems) != 1 or any(r.get("system") not in systems[0].name for r in rows):
        problems.append("the system prompt is not kept once, by its digest")
    if rows and ("Floyd" not in rows[0]["sent"] and "floyd" not in rows[0]["sent"].lower()):
        problems.append("the first line does not hold the first request")
    if len(rows) > 1 and "unified diff" not in rows[1]["sent"]:
        problems.append("the re-prompt is not what the second line holds")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", "system prompt once by digest; one line per call with what was sent and the reply")


def check_exposed_repair(work: Path) -> Result:
    """Chart audit of 26 Sep, finding 5 — Phase A asks whether DiscoPoP's pragma for the exposed
    loop can run, and asked it WITHOUT the clause repair Phase B applies: a generated
    `private(tmp)` for a variable the loop body declares fails the -fopenmp build ("use of
    undeclared identifier"), so the rewrite was reverted as `no_usable_pragma` although Phase B
    would have repaired and applied the pragma.  With the repair it is `exposed`."""
    from types import SimpleNamespace
    from ..gate import check_pragma_compiles
    from ..llm.diffs import make_diff
    from ..phases.verdicts import _verify_rewrite
    from ..pragmas import _read_tier1_patch, derive_pragma_patch
    name = "exposed repair"
    d = work / "exposed_repair"
    shutil.rmtree(d, ignore_errors=True)
    (d / ".discopop" / "patch_generator" / "7").mkdir(parents=True)
    body = ("void k(double *a, int n) {\n  for (int i = 0; i < n; i++) {\n    double tmp = a[i] * 2.0;\n"
            "    a[i] = tmp + 1.0;\n  }\n}\nint main(void) { double a[8] = {0}; k(a, 8); return 0; }\n")
    src = d / "k.c"
    src.write_text(body)
    lines = body.splitlines()
    patched = "\n".join(lines[:1] + ["#pragma omp parallel for private(tmp)"] + lines[1:]) + "\n"
    (d / ".discopop" / "patch_generator" / "7" / "1.patch").write_text(make_diff(body, patched, str(src)))
    cand = SimpleNamespace(region=SimpleNamespace(start_line=2, end_line=5, file_id=1, name="k", region_id="1:7"),
                           pattern={"pattern_id": 7, "applicable_pattern": True}, pattern_type="do_all",
                           source_file=str(src), tier=1, workload_estimate=100.0)
    raw = derive_pragma_patch(_read_tier1_patch(d / ".discopop" / "patch_generator" / "7"), str(src))
    raw_ok, _diag = check_pragma_compiles(raw or "", str(src))
    args = SimpleNamespace(source_file=str(src))
    out = _verify_rewrite([cand], (1, 6), d / ".discopop", args, None, None, None,  # type: ignore[arg-type]
                          validate_patterns=False, gate_cache={})
    if raw_ok:
        return Result(name, "skip", "the unrepaired pragma compiles here — the case does not arise")
    if out.status != "exposed":
        return Result(name, "fail", f"{out.status}: the repaired pragma was not accepted")
    return Result(name, "pass", "private(tmp) on a body-declared name fails unrepaired, is repaired, rewrite exposed")


_SHIPPED_RUN_SRC = """#include <stdio.h>
#define N 200000
static double a[N], b[N];
void back(void) {
  for (int i = N - 2; i >= 0; i--)
    a[i + 1] = a[i] + b[i];
}
int main(void) {
  for (int i = 0; i < N; i++) { a[i] = (i % 7) * 0.5; b[i] = (i % 5) * 0.25; }
  for (int r = 0; r < 10; r++) back();
  double s = 0;
  for (int i = 0; i < N; i++) s += a[i];
  printf("%.6f\\n", s);
  return 0;
}
"""
_SHIPPED_SLOW = _SHIPPED_RUN_SRC.replace(
    "void back(void) {\n  for (int i = N - 2; i >= 0; i--)\n    a[i + 1] = a[i] + b[i];\n}",
    "static double t[N];\nvoid back(void) {\n  for (int k = 0; k < 8; k++)\n    for (int i = 0; i < N; i++)\n"
    "      t[i] = a[i];\n  for (int i = N - 2; i >= 0; i--)\n    a[i + 1] = t[i] + b[i];\n}")
_SHIPPED_LEAN = _SHIPPED_RUN_SRC.replace(
    "void back(void) {\n  for (int i = N - 2; i >= 0; i--)\n    a[i + 1] = a[i] + b[i];\n}",
    "static double t[N];\nvoid back(void) {\n  for (int i = 0; i < N; i++)\n    t[i] = a[i];\n"
    "  for (int i = N - 2; i >= 0; i--)\n    a[i + 1] = t[i] + b[i];\n}")


def check_shipped_run(work: Path) -> Result:
    """D40 end to end, with DiscoPoP and the real gate; the model and the clock are stand-ins.

    A backward loop with an anti-dependence (`a[i+1] = a[i] + b[i]`).  The model's first rewrite is
    correct and exposes Do-Alls, but copies the array eight times per call; the clock says 0.4x.
    D40 must judge DiscoPoP's pragmas safe, time the rewrite WITH them against the program before
    it — while the file on disk carries no pragma — revert it, and tell the model the ratio and what
    it added; the source must be back byte for byte, and the second attempt (one copy; the clock
    says 1.6x) is kept.  The same run with --no-judge-as-shipped keeps the first rewrite, as v2 did."""
    import contextlib
    import importlib
    import io
    if not Path(_venv_bin("discopop_cxx")).exists():
        return Result("shipped run", "skip", "DiscoPoP is not installed in this venv")
    from ..args import parse_args
    from ..llm.diffs import make_diff
    agent_run: Any = importlib.import_module("discopop_agent.run")
    phase_a: Any = importlib.import_module("discopop_agent.phases.phase_a")
    name = "shipped run"
    d = work / "shipped_run"
    problems: List[str] = []
    for judged in (True, False, "depth1", "no_d41", "nospeed"):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        src = d / "k.c"
        src.write_text(_SHIPPED_RUN_SRC)
        ok, err = _profile(d, "k.c")
        if not ok:
            return Result(name, "fail", f"profile: {err}")
        calls: List[str] = []
        timed: List[Dict[str, Any]] = []

        def model(evidence: Any, model_name: str, **kw: Any) -> Any:
            msgs = kw.get("messages")
            calls.append(msgs[-1]["content"] if msgs else "(first request)")
            new = _SHIPPED_SLOW if len(calls) == 1 else _SHIPPED_LEAN
            history = (msgs or [{"role": "user", "content": "request"}]) + [{"role": "assistant", "content": "plan"}]
            return make_diff(src.read_text(), new, str(src)), history, "plan"

        def clock(before: str, after: str, source_file: str, binary_args: Any = None,
                  pairs: int = 5, extra_flags: Any = None) -> "Tuple[bool, float, str]":
            timed.append({"disk_pragma": "#pragma omp" in src.read_text(),
                          "staged_pragma": "#pragma omp" in after, "before_original": before == _SHIPPED_RUN_SRC})
            return True, (0.4 if len(timed) == 1 else 1.6), ""

        argv = ["x", "--discopop-dir", str(d / ".discopop"), "--source-file", str(src),
                "--provider", "claude-agent-sdk", "--model", "m", "--edit-mode", "direct",
                "--exclude-functions", "main", "--budget", "2"] + (
                    ["--no-judge-as-shipped"] if judged is False else
                    ["--restructure-depth", "1"] if judged == "depth1" else
                    ["--no-phase-b-reuse-d40"] if judged == "no_d41" else
                    ["--no-require-speedup"] if judged == "nospeed" else [])
        saved = (phase_a.call_llm, phase_a.measure_marginal, sys.argv)
        log = io.StringIO()
        try:
            phase_a.call_llm, phase_a.measure_marginal, sys.argv = model, clock, argv
            with contextlib.redirect_stdout(log):
                agent_run.run(parse_args())
        finally:
            phase_a.call_llm, phase_a.measure_marginal, sys.argv = saved
        text = log.getvalue()
        if judged == "nospeed":
            # The author (26 Sep): D40's SAFETY half with the speed check off too (E2-B1); nothing timed,
            # so the slow rewrite is kept after one call.
            if "D40 verdict: safe" not in text or timed or len(calls) != 1:
                problems.append(f"--no-require-speedup: {len(calls)} call(s), {len(timed)} timing(s), "
                                "no 'D40 verdict: safe' — the safety half must run, the speed half not")
        elif judged == "depth1":
            # D40.1 (a): depth 1 follows the first rewrite, so D40 judges only its SAFETY — the
            # slow rewrite is kept (speed waits for the last level), nothing is timed for it.
            first = text.split("D40 verdict:", 1)[1][:40] if "D40 verdict:" in text else ""
            if not first.strip().startswith("safe_deferred"):
                problems.append(f"depth 1: the first rewrite's D40 verdict is {first.strip()[:30]!r}, "
                                "not safe_deferred")
            if "depth 1 follows, so the speed half waits" not in text:
                problems.append("depth 1: the log does not say the speed half waits for the last level")
        elif judged == "no_d41":
            # D41 off (agent v3): Phase B times the kept rewrite's pragma again, one by one.
            phase_b = text.split("PHASE B", 1)[1] if "PHASE B" in text else ""
            if "D41" in phase_b or "marginal" not in phase_b:
                problems.append("--no-phase-b-reuse-d40: Phase B did not judge the pragma by itself")
        elif judged:
            phase_b = text.split("PHASE B", 1)[1] if "PHASE B" in text else ""
            # D41: the kept rewrite's set is applied as D40 judged it — no second timing — and the
            # noise threshold D40 measured is reused.
            if "APPLIED as D40 judged it" not in phase_b or "marginal" in phase_b.split("APPLIED as D40", 1)[0]:
                problems.append("judged: Phase B did not apply D40's set as one unit (D41)")
            if "reusing the run's threshold" not in phase_b:
                problems.append("judged: Phase B measured the noise threshold again (D41)")
            if len(calls) != 2:
                problems.append(f"judged: {len(calls)} model call(s), expected 2 (revert, then a retry)")
            if "D40 verdict: not_faster 0.40×" not in text or "D40 verdict: ok 1.60×" not in text:
                problems.append("judged: the log lacks the not_faster then ok verdicts")
            if not timed or any(t["disk_pragma"] or not t["staged_pragma"] or not t["before_original"] for t in timed):
                problems.append(f"judged: timed with a pragma on disk, none staged, or not against the program "
                                f"before the rewrite: {timed}")
            fb = calls[1] if len(calls) > 1 else ""
            if "0.40x" not in fb or "more loop" not in fb or "reverted" not in fb:
                problems.append(f"judged: the feedback lacks the ratio or what the rewrite added: {fb[:120]!r}")
            if "fails at '" in text:
                problems.append("judged: DiscoPoP's pragmas for the rewrite failed the safety gate")
            # D40.1: DiscoPoP's own verdict and D40's time are logged for every judged rewrite.
            if text.count("exposure verdict: exposed") != 2 or len(re.findall(r"D40 time: [0-9.]+ s", text)) != 2:
                problems.append("judged: the log lacks an exposure verdict or a D40 time for each of the two rewrites")
        else:
            if len(calls) != 1 or timed or "D40" in text:
                problems.append(f"--no-judge-as-shipped: {len(calls)} call(s), {len(timed)} D40 timing(s) — v2 "
                                "keeps the first exposed rewrite without judging it")
            if "exposure verdict: exposed" not in text or "deferred to depth" in text \
                    or "applied and judged in Phase B" not in text:
                problems.append("--no-judge-as-shipped: no exposure verdict, or the old 'deferred to depth N+1' "
                                "message instead of Phase B's")
    if problems:
        return Result(name, "fail", "; ".join(problems[:3]))
    return Result(name, "pass", "the slow rewrite reverted with its ratio and what it added (pragmas staged, none on "
                  "disk), the retry kept and its set applied by Phase B as judged (D41, threshold reused); at "
                  "--restructure-depth 1 judged for safety only (safe_deferred); --no-phase-b-reuse-d40 times it "
                  "again; --no-judge-as-shipped keeps the first rewrite as v2 did")


def check_paired_perf(work: Path) -> Result:
    """D40.1 (b): the gate's "not slower" test is paired under v3, as D40's.

    With the model writing the pragmas (`--llm-pragmas`), the gate compared the parallel run with
    the ORIGINAL's time taken at start-up — one run against another, minutes apart: the unpaired
    method Fix 89 removed from Settle — while DiscoPoP's pragmas are judged by D40, paired.  So E3's
    two pragma modes differed in the timing METHOD as well as the author.  Under v3 the gate now
    times the patched program against the text the patch applies to (the program before this
    rewrite), interleaved and paired, at the run's noise threshold; v2 (--no-judge-as-shipped)
    keeps the reference time.  The clock is a stand-in: the question is which comparison decides."""
    from types import SimpleNamespace
    from ..gate import validate as gate_validate
    from ..gate.timing import SPEED_THRESHOLD_KEY, capture_reference
    from ..gate.toolchain import _find_clangpp
    from ..llm import make_diff
    import importlib
    vmod: Any = importlib.import_module("discopop_agent.gate.validate")

    name = "paired perf"
    if _find_clangpp() is None:
        return Result(name, "skip", "no supported clang")
    d = work / "paired_perf"
    d.mkdir(parents=True, exist_ok=True)
    src = d / "k.c"
    orig = ("#include <stdio.h>\nint main(void) {\n    static double a[20000];\n"
            "    for (int i = 0; i < 20000; i++) a[i] = i * 0.5;\n    double s = 0;\n"
            "    for (int i = 0; i < 20000; i++) s += a[i];\n    printf(\"%.1f\\n\", s);\n    return 0;\n}\n")
    src.write_text(orig)
    ref_out, _t, ref_pairs = capture_reference(str(src))
    if ref_out is None:
        return Result(name, "fail", "the original did not build")
    par = orig.replace("    for (int i = 0; i < 20000; i++) a[i] = i * 0.5;",
                       "    #pragma omp parallel for\n    for (int i = 0; i < 20000; i++) a[i] = i * 0.5;")
    diff = make_diff(orig, par, str(src))
    seen: List[Dict[str, Any]] = []

    def clock(before: str, after: str, source_file: str, binary_args: Any = None,
              pairs: int = 5, extra_flags: Any = None) -> "Tuple[bool, float, str]":
        seen.append({"before_is_file": before == Path(source_file).read_text(), "after_has_pragma": "#pragma omp" in after})
        return True, ratio_now[0], ""

    def scaling(*a: Any, **k: Any) -> Any:
        return True, 2.0, 0.010, 0.005, ""             # 2x on the same binary: the scaling half passes

    ratio_now = [0.8]
    saved = (vmod.measure_marginal, vmod._measure_speedup)
    problems: List[str] = []
    try:
        vmod.measure_marginal, vmod._measure_speedup = clock, scaling
        kw: Dict[str, Any] = dict(reference_output=ref_out, reference_outputs=ref_pairs, require_speedup=True)
        slow = gate_validate(diff, str(src), paired_threshold=0.97, **kw)
        ratio_now[0] = 1.3
        fast = gate_validate(diff, str(src), paired_threshold=0.97, **kw)
        # v2: no threshold -> the start-up reference time decides (0.5 ms < the 5 ms parallel run)
        v2 = gate_validate(diff, str(src), reference_time=0.0005, **kw)
        # _validate_cached hands the threshold over only under v3, with the speed check on
        caught: List[Any] = []

        def spy(*a: Any, **k: Any) -> Any:
            caught.append(k.get("paired_threshold"))
            return SimpleNamespace(passed=True, stage="accepted", diagnostic="", evidence={})
        saved_v = vmod.validate
        vmod.validate = spy
        try:
            for judged in (True, False):
                args = SimpleNamespace(source_file=str(src), require_speedup=True, judge_as_shipped=judged,
                                       min_measured_speedup=1.0)
                vmod._validate_cached({SPEED_THRESHOLD_KEY: 0.95}, diff + ("\n" if judged else "\n\n"),
                                      args, ref_out, None, None)
        finally:
            vmod.validate = saved_v
    finally:
        vmod.measure_marginal, vmod._measure_speedup = saved
    if slow.passed or slow.stage != "performance" or "paired" not in (slow.diagnostic or ""):
        problems.append(f"a program at 0.80x of the one before it was not refused, paired: {slow.stage} {slow.diagnostic[:80]!r}")
    if not fast.passed:
        problems.append(f"a program at 1.30x was refused: {fast.stage} {fast.diagnostic[:80]!r}")
    if not seen or not all(x["before_is_file"] and x["after_has_pragma"] for x in seen):
        problems.append(f"not timed against the text the patch applies to: {seen}")
    if v2.passed or "ORIGINAL" not in (v2.diagnostic or ""):
        problems.append(f"v2 no longer judges against the start-up reference: {v2.stage} {v2.diagnostic[:80]!r}")
    if caught != [0.95, None]:
        problems.append(f"_validate_cached passed {caught}, expected [0.95, None] (v3 then v2)")
    if problems:
        return Result(name, "fail", "; ".join(problems[:3]))
    return Result(name, "pass", "v3's gate refuses 0.80x and keeps 1.30x of the program before the rewrite, "
                  "timed paired against the text the patch applies to; v2 still uses the start-up time")


_REQUEUE_SRC = """#include <stdio.h>
#define N 20000
static double a[N], b[N];

void kernel(int r)
{
    for (int i = 0; i < N; i++)
        a[i] = b[i] * 2.0 + r;
}

int main(void)
{
    for (int i = 0; i < N; i++) b[i] = i * 0.5;
    for (int r = 0; r < 20; r++) kernel(r);
    double s = 0.0;
    for (int i = 0; i < N; i++) s += a[i];
    printf("%.3f\\n", s);
    return 0;
}
"""


def check_requeue(work: Path) -> Result:
    """Agent v3.1, the re-queue, end to end with DiscoPoP; the gate's verdict and the model are
    stand-ins.  `kernel`'s loop is a genuine Do-All, so DiscoPoP reports it Tier 1.  When the
    safety gate refuses DiscoPoP's pragma for it (the stand-in says 'correctness', as the real gate
    said for hotspot's false Do-All in E1), the region must go to the model, whose request says
    why; when the gate accepts it, it is deferred to Phase B as before; and --no-requeue-rejected
    defers it without asking the gate (agent v3)."""
    import contextlib
    import importlib
    import io
    from types import SimpleNamespace
    if not Path(_venv_bin("discopop_cxx")).exists():
        return Result("requeue", "skip", "DiscoPoP is not installed in this venv")
    from ..args import parse_args
    agent_run: Any = importlib.import_module("discopop_agent.run")
    phase_a: Any = importlib.import_module("discopop_agent.phases.phase_a")
    name = "requeue"
    d = work / "requeue"
    problems: List[str] = []
    for case in ("refused", "accepted", "off"):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
        src = d / "k.c"
        src.write_text(_REQUEUE_SRC)
        ok, err = _profile(d, "k.c")
        if not ok:
            return Result(name, "fail", f"profile: {err}")
        requests: List[str] = []
        asked: List[str] = []

        def model(evidence: Any, model_name: str, **kw: Any) -> Any:
            msgs = kw.get("messages")
            requests.append(msgs[-1]["content"] if msgs else str(kw.get("user_prompt") or evidence))
            return "", (msgs or []) + [{"role": "assistant", "content": "plan"}], "plan"

        real = phase_a._validate_cached

        def gate(cache: Any, diff: str, args: Any, *a: Any, **k: Any) -> Any:
            if k.get("mode") == "safety" and diff.count("+") and "pragma omp" in diff:
                asked.append(diff)
                if case == "refused":
                    return (SimpleNamespace(passed=False, stage="correctness", evidence={},
                                            diagnostic="Program output changed — value 3 moved"), False, False)
                return SimpleNamespace(passed=True, stage="accepted", diagnostic="", evidence={}), False, False
            return real(cache, diff, args, *a, **k)

        argv = ["x", "--discopop-dir", str(d / ".discopop"), "--source-file", str(src),
                "--provider", "claude-agent-sdk", "--model", "m", "--edit-mode", "direct",
                "--exclude-functions", "main", "--budget", "1", "--no-require-speedup"] + (
                    ["--no-requeue-rejected"] if case == "off" else [])
        saved = (phase_a.call_llm, phase_a._validate_cached, sys.argv)
        log = io.StringIO()
        try:
            phase_a.call_llm, phase_a._validate_cached, sys.argv = model, gate, argv
            with contextlib.redirect_stdout(log):
                agent_run.run(parse_args())
        except SystemExit:
            pass
        finally:
            phase_a.call_llm, phase_a._validate_cached, sys.argv = saved
        text = log.getvalue()
        phase_a_text = text.split("PHASE B", 1)[0]
        if case == "refused":
            if "requeued for the model" not in phase_a_text or not requests:
                problems.append(f"refused: the region was not requeued ({len(requests)} model call(s))")
            elif "fails the check at 'correctness'" not in requests[0] or "DiscoPoP reports this region parallel" not in requests[0]:
                problems.append(f"refused: the request does not say why the region is here: {requests[0][-300:]!r}")
        else:
            # The loop's region only: `kernel` itself (a function DiscoPoP finds nothing in) is
            # Tier 2 in every case and gets its own call.
            loop_asked = [r for r in requests if "DiscoPoP reports this region parallel" in r]
            if loop_asked or "requeued" in phase_a_text or "deferred to Phase B" not in phase_a_text:
                problems.append(f"{case}: the Do-All loop was requeued or not deferred to Phase B")
            if case == "accepted" and not asked:
                problems.append("accepted: the gate was never asked about DiscoPoP's pragma")
            if case == "off" and asked:
                problems.append("--no-requeue-rejected: the Tier-1 pre-check ran (v3 has none)")
    if problems:
        return Result(name, "fail", "; ".join(problems[:3]))
    return Result(name, "pass", "a Tier-1 region whose DiscoPoP pragma the gate refuses goes to the model, told why; "
                  "a safe one is deferred to Phase B; --no-requeue-rejected defers without the pre-check (v3)")


_B8_HEADER = """#include <stdio.h>
#define N 4000
static double a[N], b[N], c[N], d[N], e[N];
static int setup(void)
{
    for (int i = 0; i < N; i++) { a[i] = 0.5 + i % 7; b[i] = 1.0 + i % 5; c[i] = 0.25; d[i] = 0.5; e[i] = 0.75; }
    return 0;
}
static void report(void)
{
    double s = 0.0;
    for (int i = 0; i < N; i++) s += a[i] + b[i];
    printf("%.6f\\n", s);
}
"""
_B8_KERNEL = """#include "b8/h.h"
static void kernel(int reps)
{
    for (int nl = 0; nl < reps; nl++) {
        for (int i = 1; i < N - 1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
            b[i] = b[i + 1] - e[i] * d[i];
        }
    }
}
int main(void) { if (setup()) return 1; kernel(3); report(); return 0; }
"""


def check_b8_outside_root(work: Path) -> Result:
    """DiscoPoP bug B8, fixed 26 Sep in the profiler: a call into a function defined in the translation
    unit but OUTSIDE the project root (not instrumented) used to enter the callee's call state for good —
    no instrumented exit left it — so every later access, the kernel's included, carried the callee's call
    path; the explorer then placed none of the kernel's dependences in its loop and reported TSVC s211's
    recurrence as Do-All.  Here `setup` lives in a header in a directory beside the work directory
    (reached through CPATH, as packaging v4's harness): the kernel's dependence on `b` must be recorded
    under the kernel's call path, and neither kernel loop may be Do-All."""
    if not Path(_venv_bin("discopop_cxx")).exists():
        return Result("b8 outside root", "skip", "DiscoPoP is not installed in this venv")
    name = "b8 outside root"
    base = work / "b8_outside_root"
    shutil.rmtree(base, ignore_errors=True)
    inc = base / "include" / "b8"
    d = base / "pkg"
    inc.mkdir(parents=True)
    d.mkdir(parents=True)
    (inc / "h.h").write_text(_B8_HEADER)
    (d / "k.c").write_text(_B8_KERNEL)
    saved = os.environ.get("CPATH")
    os.environ["CPATH"] = str(base / "include")
    try:
        ok, err = _profile(d, "k.c", hotspots=False)
    finally:
        if saved is None:
            os.environ.pop("CPATH", None)
        else:
            os.environ["CPATH"] = saved
    if not ok:
        return Result(name, "fail", f"profile: {err}")
    prof = d / ".discopop" / "profiler"
    states = {}
    for line in (prof / "stateID_to_callpath_mapping.txt").read_text().splitlines():
        parts = line.split()
        if len(parts) >= 2 and not line.startswith("#"):
            states[parts[0]] = parts[1]
    b_states = set(re.findall(r"@(\d+)\|GEPRESULT_[^ ]*\bb\b|RAW \d+@(\d+)\|GEPRESULT__ZL1b",
                              (prof / "dynamic_dependencies.txt").read_text()))
    paths = {states.get(x or y, "?") for x, y in b_states}
    problems: List[str] = []
    if not paths or any("setup" in p_ for p_ in paths) or not any("kernel" in p_ for p_ in paths):
        problems.append(f"the kernel's dependences on b are recorded under {sorted(paths)[:3]}")
    pats = json.loads((d / ".discopop" / "explorer" / "patterns.json").read_text()).get("patterns", {})
    kernel_lines = {i + 1 for i, l in enumerate(_B8_KERNEL.splitlines()) if l.strip().startswith("for (int")}
    doall = {int(str(x.get("start_line", "0:0")).split(":")[1]) for x in pats.get("do_all", [])
             if str(x.get("applicable_pattern")) == "True"}
    if kernel_lines & doall:
        problems.append(f"the recurrence's loops at k.c {sorted(kernel_lines & doall)} are reported Do-All")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", "a function outside the project root no longer captures the call state: the kernel's "
                  "dependence on b carries the kernel's call path, and the recurrence is not Do-All")


_B9_PROGRAM = """#include <stdio.h>
#define N 2000
static double a[N], b[N];
static unsigned long cnt = 0;
static double acc = 0.0;
static void mix(int nl)
{
    long k = ((long)nl * 7919L + 13L) % N;
    a[k] += 0.25; b[k] += 0.25;
}
static void emit(double v)
{
    cnt++;
    acc += v * (double)(cnt % 7 + 1);
}
static double sq(double v)
{
    double t = v * v;
    return t * 0.5;
}
static void kernel(int reps)
{
    for (int nl = 0; nl < reps; nl++) {
        for (int i = 0; i < N; i++) {
            a[i] = b[i] * 0.5 + 1.0;
        }
        mix(nl);
    }
    for (int i = 0; i < N; i++) {
        emit(a[i]);
    }
    for (int i = 0; i < N; i++) {
        a[i] = sq(b[i]);
    }
}
int main(void)
{
    for (int i = 0; i < N; i++) { a[i] = 0.5 + i % 7; b[i] = 1.0 + i % 5; }
    kernel(6);
    printf("%lu %.6f %.6f\\n", cnt, acc, a[0] + a[N - 1]);
    return 0;
}
"""


def check_b9_callee_in_loop(work: Path) -> Result:
    """DiscoPoP bug B9, fixed 26 Sep in the explorer: the accesses a function makes when it is called
    inside a loop iteration were attached to no task-graph context (its call-path state
    `f_loopstate…-->call_N-->callee` kept the matched loop state in front of the call, so the call
    never matched), and a loop carrying a dependence through the callee was reported Do-All — every
    TSVC package's repetition loop, whose `pb_mix(nl)` changes what the next repetition reads.  Here:
    the repetition loop calling `mix` and the loop calling the counter `emit` must NOT be Do-All; the
    loop calling the pure `sq` (only its own locals, fresh per call) must stay Do-All."""
    if not Path(_venv_bin("discopop_cxx")).exists():
        return Result("b9 callee in loop", "skip", "DiscoPoP is not installed in this venv")
    name = "b9 callee in loop"
    d = work / "b9_callee_in_loop"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    (d / "k.c").write_text(_B9_PROGRAM)
    ok, err = _profile(d, "k.c", hotspots=False)
    if not ok:
        return Result(name, "fail", f"profile: {err}")
    lines = _B9_PROGRAM.splitlines()
    loop_at = {}
    for i, l in enumerate(lines):
        if l.strip().startswith("for (int nl"):
            loop_at["repetition (mix)"] = i + 1
        elif l.strip().startswith("for (int i") and i + 1 < len(lines):
            body = lines[i + 1].strip()
            if body.startswith("emit("):
                loop_at["counter (emit)"] = i + 1
            elif body.startswith("a[i] = sq("):
                loop_at["pure (sq)"] = i + 1
    pats = json.loads((d / ".discopop" / "explorer" / "patterns.json").read_text()).get("patterns", {})
    doall = {int(str(x.get("start_line", "0:0")).split(":")[1]) for x in pats.get("do_all", [])
             if str(x.get("applicable_pattern")) == "True"}
    problems = [f"the {k} loop at k.c:{loop_at[k]} is reported Do-All"
                for k in ("repetition (mix)", "counter (emit)") if loop_at[k] in doall]
    if loop_at["pure (sq)"] not in doall:
        problems.append(f"the pure (sq) loop at k.c:{loop_at['pure (sq)']} is no longer Do-All")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", "a callee's accesses inside a loop iteration are placed in that iteration: the loops "
                  "carrying a dependence through mix and emit are not Do-All, the loop calling the pure sq still is")


_B4_PROGRAM = """#include <stdio.h>
#define N 2000
static double a[N], b[N];
static void kernel(int reps)
{
    for (int nl = 0; nl < reps; nl++) {
        for (int i = N - 2; i >= 0; i--) {
            a[i + 1] = a[i] + b[i];
        }
    }
}
int main(void)
{
    for (int i = 0; i < N; i++) { a[i] = 0.5 + i % 7; b[i] = 1.0e-3 * (i % 5); }
    kernel(6);
    printf("%.6f %.6f\\n", a[1], a[N - 1]);
    return 0;
}
"""


def check_b4_nested_duplication(work: Path) -> Result:
    """DiscoPoP bug B4, fixed 26 Sep in the explorer: the task graph duplicates each loop's iteration
    once, and an enclosing loop's copy took the loops inside it as they were at that moment — an
    inner loop not yet duplicated stayed one iteration there, so only its first iteration's call-path
    states found a place, and the recurrence carried between its later iterations was lost. Which
    loop came first followed a set's order: TSVC s112's inner recurrence was Do-All in 7 of 8 runs
    on one profile. Here the same shape; the explorer runs three times on one profile and the inner
    recurrence must be blocked every time, with no "Applied fix" warning (the uncopied inner loop's
    missing iteration ids)."""
    if not Path(_venv_bin("discopop_cxx")).exists():
        return Result("b4 nested duplication", "skip", "DiscoPoP is not installed in this venv")
    name = "b4 nested duplication"
    d = work / "b4_nested_duplication"
    shutil.rmtree(d, ignore_errors=True)
    d.mkdir(parents=True)
    (d / "k.c").write_text(_B4_PROGRAM)
    ok, err = _profile(d, "k.c", hotspots=False)
    if not ok:
        return Result(name, "fail", f"profile: {err}")
    inner = next(i + 1 for i, l in enumerate(_B4_PROGRAM.splitlines()) if l.strip().startswith("for (int i = N - 2"))
    problems: List[str] = []
    for run in range(1, 4):
        shutil.rmtree(d / ".discopop" / "explorer", ignore_errors=True)
        ok, err = _run([_venv_bin("discopop_explorer")], d / ".discopop")
        if not ok:
            return Result(name, "fail", f"explorer run {run}: {err[-200:]}")
        pats = json.loads((d / ".discopop" / "explorer" / "patterns.json").read_text()).get("patterns", {})
        doall = {int(str(x.get("start_line", "0:0")).split(":")[1]) for x in pats.get("do_all", [])
                 if str(x.get("applicable_pattern")) == "True"}
        if inner in doall:
            problems.append(f"run {run}: the recurrence at k.c:{inner} is reported Do-All")
        if "set previously unspecified loopstate iteration id" in err:
            problems.append(f"run {run}: an inner loop was copied without its iterations")
    if problems:
        return Result(name, "fail", "; ".join(problems))
    return Result(name, "pass", "inner loops are duplicated before the loops that enclose them: the recurrence is "
                  "blocked in 3 of 3 explorer runs on one profile")


_CHECKS: List[Tuple[str, Callable[[Path], Result]]] = [
    ("impact", check_impact_ranking),
    ("min-impact", check_min_impact),
    ("new-region-ranking", check_new_region_ranking),
    ("hotspot-remeasure", check_hotspot_remeasure),
    ("explorer-stall", check_explorer_stall),
    ("loop-counts", check_loop_counts),
    ("covered-skip", check_covered_skip),
    ("budget-policy", check_budget_policy),
    ("project-mode", check_project_mode),
    ("pattern-choice", check_pattern_choice),
    ("prompt-truth", check_prompt_truth),
    ("prompt-ablation", check_prompt_ablation),
    ("bare-llm", check_bare_llm),
    ("bare-speed-off", check_bare_speed_off),
    ("workspace-confined", check_workspace_confined),
    ("twin-prompt", check_twin_prompt),
    ("twin-run", check_twin_run),
    ("harness-lines", check_harness_lines),
    ("evidence-enrich", check_evidence_enrichment),
    ("dep-standing", check_dependence_standing),
    ("schedule-runtime", check_schedule_runtime),
    ("noise-floor-inputs", check_noise_floor_inputs),
    ("hotspot-remap", check_hotspot_remap),
    ("mixed-rank", check_mixed_scale_ranking),
    ("fast-refresh", check_fast_refresh),
    ("fast-refresh-eq", check_fast_refresh_equivalence),
    ("reduction-carry", check_reduction_carry),
    ("clause", check_clauses),
    ("dep-review", check_dep_review),
    ("tsan", check_tsan_barrier),
    ("equivalence", check_output_equivalence),
    ("noise-floor", check_noise_floor),
    ("schedule-stress", check_schedule_stress),
    ("anchor-vs-ref", check_anchor_correctness),
    ("dep-evidence", check_dependence_evidence),
    ("dep-lines", check_dep_line_resolution),
    ("timing-size", check_timing_size),
    ("omp-include", check_omp_include),
    ("omp-runtime", check_omp_runtime),
    ("exclude-cxx", check_exclude_cxx),
    ("explorer-multi-backedge", check_explorer_multi_backedge),
    ("profiler-else-loop", check_profiler_else_loop),
    ("pragma-sibling-loops", check_pragma_sibling_loops),
    ("pragma-arbitration", check_pragma_arbitration),
    ("arg-dependencies", check_arg_dependencies),
    ("settle-paired", check_settle_paired),
    ("phase-b-joint", check_phase_b_joint),
    ("dp-floor", check_dp_floor),
    ("shipped-prompt", check_shipped_prompt),
    ("shipped-judge", check_shipped_judge),
    ("request-log", check_request_log),
    ("exposed-repair", check_exposed_repair),
    ("shipped-run", check_shipped_run),
    ("paired-perf", check_paired_perf),
    ("requeue", check_requeue),
    ("b8-outside-root", check_b8_outside_root),
    ("b9-callee-in-loop", check_b9_callee_in_loop),
    ("b4-nested-duplication", check_b4_nested_duplication),
]


def main() -> int:
    p = argparse.ArgumentParser(description="Deterministic feature checks (no LLM)")
    p.add_argument("--only", nargs="*", default=None,
                   help=f"run a subset: {', '.join(k for k, _ in _CHECKS)}")
    p.add_argument("--keep", action="store_true", help="keep the working directory")
    a = p.parse_args()

    selected = [(k, fn) for k, fn in _CHECKS if not a.only or k in a.only]
    work = Path(tempfile.mkdtemp(prefix="dp_features_"))
    print(f"\n  Feature checks — working in {work}\n")

    results: List[Result] = []
    for key, fn in selected:
        try:
            r = fn(work)
        except Exception as e:                       # noqa: BLE001 - reported as a failure
            r = Result(key, "fail", f"{type(e).__name__}: {e}")
        results.append(r)
        mark = {"pass": "  ok  ", "fail": " FAIL ", "skip": " skip "}[r.status]
        print(f"  [{mark}] {r.name:<20} {r.detail}")

    if not a.keep:
        shutil.rmtree(work, ignore_errors=True)

    passed = sum(1 for r in results if r.status == "pass")
    failed = sum(1 for r in results if r.status == "fail")
    skipped = sum(1 for r in results if r.status == "skip")
    print(f"\n  {passed} passed, {failed} failed, {skipped} skipped\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
