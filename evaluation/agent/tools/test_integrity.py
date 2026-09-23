#!/usr/bin/env python3
"""Tests for the package/profile integrity guard in cli.py (`check_package`).

Run: `python3 agent/tools/test_integrity.py` (exit status 1 on any failure). No model and
no DiscoPoP are needed: the profiler and the agent are replaced by stubs, and the guard is
exercised through the real `cmd_run` loop on temporary copies of the packaged calibration
benchmark `calib/vecsum` (and `calib/vecsum_proj` for the project layout).

What must hold (THESIS_EXPERIMENTS.md §5j):
  1. every prepared package matches the digest its packager wrote;
  2. a modified package stops a run before anything is taken from it;
  3. a trial that modifies the archived sources or the archived profile keeps its own
     record (it ran on an intact copy) and stops the run — the next trial never starts;
  4. an intact run records the before/after checks with every trial.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

sys.path[:0] = [str(Path(__file__).resolve().parent), str(Path(__file__).resolve().parents[2] / "shared")]
import cli  # noqa: E402

AGENT_DIR = Path(__file__).resolve().parents[1]
PREPARED = AGENT_DIR / "prepared"
RUNS = AGENT_DIR / "runs"
fails = 0


def expect(label: str, cond: bool, detail: str = "") -> None:
    global fails
    fails += not cond
    print(f"  [{'pass' if cond else 'FAIL'}] {label}{(' — ' + detail) if detail and not cond else ''}")


# ---- 1. every package matches its packager's digest ------------------------------------
print("1. prepared packages")
n = 0
for meta_p in sorted(PREPARED.rglob("meta.json")):
    meta = json.loads(meta_p.read_text())
    rec = cli.check_package(meta_p.parent.name, meta_p.parent, when="test")
    n += 1
    if meta.get("output_sha256") is None:
        expect(f"{meta_p.parent} carries a digest", False)
expect(f"{n} packages match their packager's digest", n > 0)


# ---- 1b. no answer in what the model reads (record §1a, D36) ---------------------------
# Until TSVC generator v3 (23 Sep) every TSVC source opened with TSVC's category comment and
# this harness's `class:` / `transformation:` labels — the solving transformation, read by the
# model in every arm of E1, E1-bare and E2. A package's SOURCES are what the model's workspace
# holds; meta.json is not. Calibration packages describe their task by design and never enter
# an experiment (prepare_calib.py), so they are left out.
print("1b. no solution vocabulary in package sources")
import re  # noqa: E402

LABELS = re.compile(r"transformation\s*:|class\s*:\s*(restructure|annotate|decline)", re.I)
TSVC_WORDS = ["statement reordering", "loop distribution", "node splitting", "scalar expansion",
              "loop peeling", "peeling", "index-set", "induction variable", "loop reversal",
              "carry-around", "wrap-around", "crossing threshold", "compaction", "prefix sum",
              "recurrence", "max-index", "search loop", "packing", "reduction"]
SOURCE_EXT = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp"}
checked, leaks = 0, []
for meta_p in sorted(PREPARED.rglob("meta.json")):
    pkg = meta_p.parent
    if pkg.relative_to(PREPARED).parts[0] == "calib":
        continue
    meta = json.loads(meta_p.read_text())
    words = list(TSVC_WORDS) if meta.get("suite") == "tsvc" else []
    for key in ("transformation", "why", "category"):
        v = str(meta.get(key) or "").strip()
        if meta.get("suite") == "tsvc" and len(v) > 12:
            words.append(v)
    for f in sorted(p for p in pkg.rglob("*") if p.suffix in SOURCE_EXT):
        text = f.read_text(errors="replace")
        checked += 1
        if LABELS.search(text):
            leaks.append(f"{f.relative_to(PREPARED)}: a class/transformation label")
        low = text.lower()
        hit = next((w for w in words if w.lower() in low), None)
        if hit:
            leaks.append(f"{f.relative_to(PREPARED)}: '{hit}'")
expect(f"{checked} package sources carry no solution vocabulary", checked > 0 and not leaks,
       "; ".join(leaks[:4]) + (f" (+{len(leaks) - 4} more)" if len(leaks) > 4 else ""))


# ---- 2–4. the guard through the real run loop, profiler and agent stubbed -------------
def fake_profile_once(bench_dir, src_name, dest, agent_repo, timeout):
    """Stand-in for DiscoPoP: archive the sources exactly as profile_once does, plus a
    small fake profile tree."""
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(bench_dir / "meta.json", dest / "meta.json")
    if cli._project_of(bench_dir) is None:
        shutil.copy2(bench_dir / src_name, dest / src_name)
    else:
        cli._copy_tree(bench_dir, dest)
    dp = dest / ".discopop"
    (dp / "explorer").mkdir(parents=True)
    (dp / "FileMapping.txt").write_text(f"1\t{dest / src_name}\n")
    (dp / "explorer" / "patterns.json").write_text('{"patterns": {"do_all": []}}')
    return {"wrapper": "stub", "profile_sha256": cli._tree_digest(dp)}


class Damage:
    """What the stubbed agent does to the archived copies: nothing, or one corruption."""
    kind = "none"
    calls = 0


def fake_run_trial(bench, bench_dir, profile_dir, trial, arm, arm_flags, model, a, cc, cxx):
    Damage.calls += 1
    trial.mkdir(parents=True, exist_ok=True)
    src = cli._source_name(bench_dir)
    if Damage.kind == "source":
        p = profile_dir / src
        p.write_text(p.read_text() + "\n/* a trial wrote here */\n")
    elif Damage.kind == "profile":
        (profile_dir / ".discopop" / "explorer" / "patterns.json").write_text('{"patterns": {}}')
    return {"benchmark": bench, "kernel": bench_dir.name, "arm": arm, "model": model,
            "status": "agent_error", "agent_error": "stub agent"}


cli.profile_once = fake_profile_once
cli.run_trial = fake_run_trial


def run(run_id: str, bench: str, trials: int) -> int:
    shutil.rmtree(RUNS / run_id, ignore_errors=True)
    a = argparse.Namespace(
        benchmarks=[bench], arms=["full"], models=["stub"], trials=trials,
        provider="none", edit_mode="direct", agent_arg=[], agent_repo=str(cli.DEFAULT_AGENT_REPO),
        cc=None, cxx=None, verify_size="SMALL", threads=[2], repeats=1, timeout=60,
        run_id=run_id, keep_work=False, min_runtime_share=0.0, check_seed="7")
    return cli.cmd_run(a)


def trial_records(run_id: str):
    return sorted((RUNS / run_id / "benchmarks").rglob("trial.json"))


def manifest_status(run_id: str) -> str:
    m = json.loads((RUNS / run_id / "manifest.json").read_text())
    return m.get("status") or m.get("finished", {}).get("status", "?")


for layout, bench in (("single", "calib/vecsum"), ("project", "calib/vecsum_proj")):
    print(f"\n2. intact run, {layout} layout ({bench})")
    Damage.kind, Damage.calls = "none", 0
    rc = run("_test_integrity", bench, 2)
    recs = [json.loads(p.read_text()) for p in trial_records("_test_integrity")]
    expect("exit status 0", rc == 0, str(rc))
    expect("both trials ran", Damage.calls == 2 and len(recs) == 2, f"{Damage.calls} {len(recs)}")
    expect("before/after checks recorded with every trial",
           all(r.get("package_integrity", {}).get("before", {}).get("ok")
               and r["package_integrity"].get("after", {}).get("ok") for r in recs))
    expect("archived sources and profile digests recorded",
           all(r["package_integrity"]["after"].get("archived_sha256")
               and r["package_integrity"]["after"].get("profile_sha256") for r in recs))
    expect("run finished", manifest_status("_test_integrity") == "finished",
           manifest_status("_test_integrity"))

    for kind in ("source", "profile"):
        print(f"\n3. a trial modifies the archived {kind}, {layout} layout")
        Damage.kind, Damage.calls = kind, 0
        rc = run("_test_integrity", bench, 3)
        recs = [json.loads(p.read_text()) for p in trial_records("_test_integrity")]
        expect("exit status 2", rc == 2, str(rc))
        expect("only the first trial ran — the run stopped before the second",
               Damage.calls == 1, str(Damage.calls))
        expect("the damaging trial's own record is kept", len(recs) == 1, str(len(recs)))
        expect("its after-check names the corruption",
               bool(recs) and recs[0]["package_integrity"]["after"].get("ok") is False
               and kind in recs[0]["package_integrity"]["after"].get("error", ""))
        expect("run status aborted_package_corrupted",
               manifest_status("_test_integrity") == "aborted_package_corrupted",
               manifest_status("_test_integrity"))

print("\n4. a modified package stops the run before anything is taken from it")
Damage.kind, Damage.calls = "none", 0
bench_dir = PREPARED / "calib" / "vecsum"
src = bench_dir / "vecsum.c"
keep = src.read_bytes()
try:
    src.write_bytes(keep + b"\n/* modified package */\n")
    rc = run("_test_integrity", "calib/vecsum", 1)
    expect("exit status 2", rc == 2, str(rc))
    expect("no trial ran", Damage.calls == 0, str(Damage.calls))
    expect("no profile was taken", not (RUNS / "_test_integrity" / "profiles").exists()
           or not list((RUNS / "_test_integrity" / "profiles").rglob("profile.json")))
finally:
    src.write_bytes(keep)
rec = cli.check_package("vecsum", bench_dir, when="test")
expect("package restored", rec["ok"])
shutil.rmtree(RUNS / "_test_integrity", ignore_errors=True)

print(f"\n{'ALL PASS' if not fails else f'{fails} FAILURE(S)'}")
sys.exit(1 if fails else 0)
