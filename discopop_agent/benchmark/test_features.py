"""
Feature regression suite — verifies the agent's machinery without an LLM
------------------------------------------------------------------------
The existing benchmark (`benchmark/run.py`) measures how well a MODEL does on
parallelization cases: it needs an API key, takes minutes, and its results move
with the model.  This suite is the other half — it checks the parts of the agent
that are supposed to be deterministic, and it must pass on every commit:

  * impact ranking    the queue is ordered by measured time, not instruction count
  * min-impact        a region too small to pay off is dropped before any LLM call
  * fast refresh      an edit that changes nothing loses no dependence data
  * clause checks     the pragma defects that compile, run and print the right answer
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
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..fast_refresh import line_map, remap_dependencies, verify_translation
from ..impact import load_hotspots
from ..l1_planner import build_candidates
from ..l3_llm import make_diff
from ..l4_validator import _find_clangpp, _macos_sysroot_flag, find_archer

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
    from ..controller import check_llm_pragmas

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
    from ..controller import _is_omp_barrier_false_positive

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


_CHECKS: List[Tuple[str, Callable[[Path], Result]]] = [
    ("impact", check_impact_ranking),
    ("min-impact", check_min_impact),
    ("fast-refresh", check_fast_refresh),
    ("clause", check_clauses),
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
