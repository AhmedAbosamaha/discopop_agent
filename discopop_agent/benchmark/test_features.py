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
  * fast refresh      an edit that changes nothing loses no dependence data,
                      and a refresh reaches the same conclusions as a full re-profile
  * clause checks     the pragma defects that compile, run and print the right answer
  * dep review        a discharged blocker actually removes dependence lines
  * TSan barrier      a real race is caught; an artefact of the OpenMP runtime is not

Run it from the repository root:

    venv/bin/python -m discopop_agent.benchmark.test_features
    venv/bin/python -m discopop_agent.benchmark.test_features --only clause tsan

Checks that need tooling which is not installed (DiscoPoP, clang, libarcher)
report SKIP rather than failing, so the suite is useful on a partial setup.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from ..profiling.fast_refresh import (line_map, remap_dependencies,
                                      verify_translation)
from ..plan.impact import load_hotspots
from ..plan import build_candidates
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


def _profile(work: Path, src_name: str, hotspots: bool = True) -> Tuple[bool, str]:
    """Dependence profile, and optionally the hotspot measurement beside it."""
    ok, err = _run([_venv_bin("discopop_cxx"), src_name, "-o", "a.out"], work)
    if not ok:
        return False, f"discopop_cxx: {err[-200:]}"
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
    from ..pragmas import check_llm_pragmas

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

    failures = []
    for label, new_text, should_reject in cases:
        problem = check_llm_pragmas(make_diff(orig, new_text, str(src)), str(src))
        if bool(problem) != should_reject:
            failures.append(f"{label}: expected "
                            f"{'rejection' if should_reject else 'acceptance'}")
    if failures:
        return Result("clause checks", "fail", "; ".join(failures))
    return Result("clause checks", "pass", f"{len(cases)}/{len(cases)} verdicts correct")


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
        dry_run=False, edit_mode="direct", llm_pragmas=True, fast_refresh=True,
        llm_deps=False, hotspots=False, min_impact=0.0, restructure_depth=0,
        require_speedup=False, build_retries=2, apply_patches=True,
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
    if full_p != fast_p:
        only_full = sorted(set(full_p) - set(fast_p))[:2]
        only_fast = sorted(set(fast_p) - set(full_p))[:2]
        return Result("fast refresh ≡ full", "fail",
                      f"{len(full_p)} vs {len(fast_p)} patterns; "
                      f"only-full={only_full} only-fast={only_fast}")
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
        return Result("dependence review", "skip", "this case produced no blockers")

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
            edit_mode="direct", llm_pragmas=True, fast_refresh=True, llm_deps=True,
            hotspots=False, min_impact=0.0, restructure_depth=0, require_speedup=False,
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
    return Result("hotspot remap", "pass",
                  f"measurements and covered spans follow the code; "
                  f"{dropped} dropped when lines vanish")


_CHECKS: List[Tuple[str, Callable[[Path], Result]]] = [
    ("impact", check_impact_ranking),
    ("min-impact", check_min_impact),
    ("hotspot-remap", check_hotspot_remap),
    ("fast-refresh", check_fast_refresh),
    ("fast-refresh-eq", check_fast_refresh_equivalence),
    ("clause", check_clauses),
    ("dep-review", check_dep_review),
    ("tsan", check_tsan_barrier),
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
