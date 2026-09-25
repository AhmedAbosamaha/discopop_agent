#!/usr/bin/env python3
"""Tests for scaffold.py, the harness's check that a rewrite left the packaging's code alone.

Run: `python3 agent/tools/test_scaffold.py` (exit status 1 on any failure). Uses the packaged
sources, and the recorded runs `pilot2` and `local_obs1` when present. Every case states
what must be caught and what must be allowed; see THESIS_EXPERIMENTS.md for why each exists.
"""
import glob
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scaffold as S  # noqa: E402

R = str(Path(__file__).resolve().parent.parent)
fails = 0
def expect(label, res, ok):
    global fails
    good = res["ok"] == ok; fails += not good
    print(f"  [{'pass' if good else 'FAIL'}] {label}: ok={res['ok']} {res['problems'][:1]}")
n_self = 0
for meta in sorted(glob.glob(f"{R}/prepared/*/*/meta.json")):
    m = json.load(open(meta))
    if m.get("suite") == "calibration":
        continue
    f = f"{meta[:-len('meta.json')]}{m['file']}"      # the unit holding main and the harness code
    t = open(f).read(); r = S.check(t, t); n_self += 1
    if not (r["ok"] and r["applies"]): fails += 1; print("  FAIL self", f, r)
print(f"  {n_self} unchanged sources checked")
for run, name, want in [  # recorded runs: skipped when absent
("pilot2", "seidel-2d", False), ("local_obs1", "seidel-2d", False),
                        ("local_obs1", "2mm", True), ("local_obs1", "jacobi-2d-imper", True)]:
    found = glob.glob(f"{R}/runs/{run}/benchmarks/polybench/{name}/full/*/rep1")
    if not found:
        print(f"  [skip] {run} {name}: run not present")
        continue
    d = found[0]
    expect(f"{run} {name}", S.check(open(d+"/original.c").read(), open(d+"/final.c").read()), want)
# The harness judges a project on ALL its files as one text (cli._project_text ==
# bench.project_text): since D6 the timer and the digest live in pb_harness.h, not in the
# kernel file, so the cases below edit the same text the harness would see.
import bench  # noqa: E402
_sd = Path(f"{R}/prepared/polybench/seidel-2d")
src = bench.project_text(_sd, bench.load_meta(_sd))
moved = src.replace("  pb_timer_stop();\n", "", 1).replace("  pb_timer_start();\n", "  pb_timer_start();\n  pb_timer_stop();\n", 1)
expect("timer stop moved before the kernel call", S.check(src, moved), False)
expect("timer body edited", S.check(src, src.replace("CLOCK_MONOTONIC", "CLOCK_REALTIME", 1)), False)
expect("perturbation removed", S.check(src, re.sub(r"\n\s*PB_PERTURB\(A[^\n]*", "", src, 1)), False)
expect("digest edited", S.check(src, src.replace("% 9973", "% 9967", 1)), False)
expect("comment edited", S.check(src, src.replace("/* Run kernel. */", "/* Run the kernel now. */", 1)), True)
k = src.index("void kernel_seidel_2d"); body = src.index("for", k)
expect("pragma in kernel", S.check(src, src[:body] + "#pragma omp parallel for\n  " + src[body:]), True)
call = "  kernel_seidel_2d (tsteps, n, POLYBENCH_ARRAY(A));\n"
assert call in src
inline = "  {\n    int t, i, j;\n    for (t = 0; t < tsteps; t++)\n      for (i = 1; i <= n - 2; i++)\n        (*A)[i][1] = 0.5 * (*A)[i][1];\n  }\n"
expect("kernel inlined INSIDE the timer", S.check(src, src.replace(call, inline, 1)), True)
out = src.replace(call, "", 1).replace("  pb_timer_start();\n", inline + "  pb_timer_start();\n", 1)
expect("kernel inlined BEFORE the timer (moved out)", S.check(src, out), False)
before = "  {\n    int t, j;\n    for (t = 0; t < tsteps; t++)\n      for (j = 1; j <= n - 2; j++)\n        (*A)[1][j] = 0.25 * (*A)[1][j];\n  }\n"
inside = "  {\n    int i;\n    for (i = 1; i <= n - 2; i++)\n      (*A)[i][1] = 0.5 * (*A)[i][1];\n  }\n"
expect("part of the computation moved before the timer", S.check(src, src.replace(call, inside, 1).replace("  pb_timer_start();\n", before + "  pb_timer_start();\n", 1)), False)
expect("timed region emptied", S.check(src, src.replace(call, "  ;\n", 1)), False)
for app in ["burkardt/md", "rodinia-3.1/pathfinder", "npb/mg", "npb/lu", "npb/is", "rodinia-3.1/hotspot", "rodinia-3.1/nw"]:
    # the unit holding main and the harness code (a project since D6: NPB is `<B>/<b>.cpp`)
    f = f"{R}/prepared/{app}/" + json.load(open(f"{R}/prepared/{app}/meta.json"))["file"]; t = open(f).read()
    m_start = re.search(r"\n[ \t]*pb_timer_start\s*\(\s*\)\s*;", t)
    assert m_start is not None, f"{app}: no pb_timer_start"
    a = m_start.end()
    m_stop = re.search(r"\n[ \t]*pb_timer_stop\s*\(\s*\)\s*;", t[a:])
    assert m_stop is not None, f"{app}: no pb_timer_stop"
    b = m_stop.start() + a
    win = t[a:b]; m = re.search(r"\n([ \t]*)for\s*\(", win)
    if m:
        expect(f"{app} pragma in computation window", S.check(t, t[:a] + win[:m.start()] + "\n" + m.group(1) + "#pragma omp parallel for" + win[m.start():] + t[b:]), True)
    stop = m_stop.group(0)
    expect(f"{app} timer stop moved to window start", S.check(t, t[:a] + stop + win + "\n  (void)0;" + t[b + len(stop):]), False)

# How a trial counts in the statistics (main_comparison_stats.py; record §6, 25 Sep). A harness
# edit is its own row and never unusable, even when its program does not build (E2's twin_full
# s331 rep 4 was counted "did not compile"); a rewrite with no pragma has a verdict, and is
# unusable when it runs slower than the original (E2's twin_full s244 rep 1, 0.63×).
print("\ncounting")
import main_comparison_stats as M  # noqa: E402
def holds(label, cond):
    global fails
    fails += not cond
    print(f"  [{'pass' if cond else 'FAIL'}] {label}")
NOBUILD = {"status": "verify_build_failed", "build_errors": {"final_dump": "e", "final_par": "e"}}
def trial(outcome, speedup=None, verify=None, rep=1, arm="twin_full"):
    v = dict(verify or {"status": "ok"})
    if speedup is not None:
        v["par"] = {"6": {"speedup": speedup}}
    return {"arm": arm, "benchmark": "tsvc/s244", "repeat": rep, "outcome": outcome, "verify": v}
holds("harness edit that does not build: no verdict", not M._with_verdict(trial("SCAFFOLD_MODIFIED", verify=NOBUILD)))
holds("harness edit that builds: no verdict", not M._with_verdict(trial("SCAFFOLD_MODIFIED", 1.5)))
holds("changed, not parallel: a verdict", M._with_verdict(trial("changed-not-parallel", 1.04)))
holds("changed, not parallel, 1.04x: no slowdown", not M._ships_slowdown(trial("changed-not-parallel", 1.04)))
holds("changed, not parallel, 0.63x: a slowdown", M._ships_slowdown(trial("changed-not-parallel", 0.63)))
holds("parallel, 0.8x: a slowdown", M._ships_slowdown(trial("parallel-not-faster", 0.8)))
holds("FASTER: no slowdown", not M._ships_slowdown(trial("FASTER", 2.0)))
holds("unchanged: a verdict, no slowdown", M._with_verdict(trial("no-change")) and not M._ships_slowdown(trial("no-change")))
holds("final program does not build: a verdict", M._with_verdict(trial("VERIFY_FAILED", verify=NOBUILD)))
holds("original does not build: no verdict", not M._with_verdict(
    trial("VERIFY_FAILED", verify={"status": "verify_build_failed", "build_errors": {"orig_dump": "e"}})))
holds("agent error: no verdict", not M._with_verdict(trial("AGENT_ERROR")))
tw = M.three_way([trial("FASTER", 2.0, rep=1), trial("SCAFFOLD_MODIFIED", verify=NOBUILD, rep=2),
                  trial("changed-not-parallel", 0.63, rep=3), trial("no-change", arm="default"),
                  trial("no-change", arm="discopop_gate")], "default", "twin_full")
got = tw["classes"]["R"]["arms"]["model alone"] if "R" in tw["classes"] else {}
holds("three-way: 2 with a verdict, 1 harness edit, 1 unusable (the slow rewrite), 0 not compiling",
      (got.get("with_verdict"), got.get("tampered"), got.get("unusable"), got.get("did_not_compile")) == (2, 1, 1, 0))
print("\nFAILURES:", fails)
sys.exit(1 if fails else 0)
