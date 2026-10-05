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
# E2-B1's Rodinia unit comes from an OpenMP program (prepare_bfs.py): nothing of its OpenMP code and no
# comment about threads may survive the stripping (one of bfs.cpp's comments says a thread changes `stop`).
OPENMP_WORDS = ["pragma", "omp.h", "omp_", "openmp", "thread", "atomic", "critical", "parallel", "cuda"]
SOURCE_EXT = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp"}
checked, leaks = 0, []
for meta_p in sorted(PREPARED.rglob("meta.json")):
    pkg = meta_p.parent
    if pkg.relative_to(PREPARED).parts[0] == "calib":
        continue
    meta = json.loads(meta_p.read_text())
    is_tsvc = str(meta.get("suite") or "").startswith("tsvc")   # tsvc and E2-B1's tsvc_b1
    is_b1_rodinia = meta.get("suite") == "rodinia_b1"
    words = list(TSVC_WORDS) if is_tsvc else list(OPENMP_WORDS) if is_b1_rodinia else []
    for key in ("transformation", "why", "category"):
        v = str(meta.get(key) or "").strip()
        if (is_tsvc or is_b1_rodinia) and len(v) > 12:
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


# ---- 1c. every TSVC and E2-B1 package is what its packager renders now -----------------
# The packages under prepared/ are generated, not tracked; a change to the packager's shared
# templates (pb_mix, the harness, the kernel head) must not silently change a package an
# experiment already ran on. So every TSVC package on disk is rendered again and compared byte
# for byte — the source, and in layout v4 the harness header outside the package. E2-B1's
# Rodinia bfs (prepare_bfs.py, v4) the same way.
print("1c. TSVC and E2-B1 packages equal their packager's rendering")
import prepare_bfs  # noqa: E402
import prepare_tsvc  # noqa: E402

rendered, drift = 0, []
for meta_p in sorted(PREPARED.rglob("meta.json")):
    meta = json.loads(meta_p.read_text())
    suite = str(meta.get("suite") or "")
    if suite == prepare_bfs.SUITE:
        rendered += 1
        if meta_p.parent.name != prepare_bfs.NAME:
            drift.append(f"{suite}/{meta_p.parent.name}: not a package of prepare_bfs.py")
            continue
        if (meta_p.parent / meta["file"]).read_text() != prepare_bfs.render():
            drift.append(f"{suite}/{meta_p.parent.name}: source differs from the packager's")
        hdr = PREPARED / "_harness" / meta["harness"]
        if not hdr.exists() or hdr.read_text() != prepare_bfs.render_harness():
            drift.append(f"{suite}/{meta_p.parent.name}: harness header differs from the packager's")
        if meta.get("hot_loop") != prepare_bfs.hot_loop():
            drift.append(f"{suite}/{meta_p.parent.name}: meta.json's hot_loop differs from the packager's")
        continue
    if suite not in prepare_tsvc.SUITES:
        continue
    loop = {l.name: l for l in prepare_tsvc.SUITES[suite]}.get(meta_p.parent.name)
    if loop is None:
        drift.append(f"{suite}/{meta_p.parent.name}: not a loop of the packager's suite")
        continue
    src = meta_p.parent / meta["file"]
    if suite in prepare_tsvc.CLEAN:
        # packaging v5 and v6 (4 Oct): three files in the package, the measurement header outside it
        version, files_of, harness_of, _kernel_of, hot_of, ours = prepare_tsvc.CLEAN[suite]
        rendered += 1
        for fname, text in files_of(loop).items():
            if not (meta_p.parent / fname).exists() or (meta_p.parent / fname).read_text() != text:
                drift.append(f"{suite}/{loop.name}: {fname} differs from the packager's")
        hdr = PREPARED / "_harness" / meta["harness"]
        if not hdr.exists() or hdr.read_text() != harness_of(loop):
            drift.append(f"{suite}/{loop.name}: harness header differs from the packager's")
        if meta.get("hot_loop") != hot_of(loop):
            drift.append(f"{suite}/{loop.name}: meta.json's hot_loop differs from the packager's")
        if meta.get("generator_version") != version or meta.get("exclude_functions") != ours:
            drift.append(f"{suite}/{loop.name}: meta.json is not this layout's (version, the functions of main.c)")
        if (meta.get("project") or {}).get("editable") != [f"{loop.name}.c"]:
            drift.append(f"{suite}/{loop.name}: meta.json does not name the benchmark's file as the one editable file")
        continue
    v4 = bool(meta.get("harness"))
    text = prepare_tsvc.render(loop) if v4 else prepare_tsvc.render_v3(loop)
    rendered += 1
    if src.read_text() != text:
        drift.append(f"{suite}/{loop.name}: source differs from the packager's")
    if v4:
        hdr = PREPARED / "_harness" / meta["harness"]
        if not hdr.exists() or hdr.read_text() != prepare_tsvc.render_harness(loop):
            drift.append(f"{suite}/{loop.name}: harness header differs from the packager's")
    # E2-B1's hot loop (27 Sep) is read from meta.json by every trial: a package made before the
    # field existed, or from an older declaration, would record `hot_loop_covered: null` in every
    # trial — the primary outcome silently not computable. None for every other TSVC package.
    if meta.get("hot_loop") != prepare_tsvc.hot_loop(loop):
        drift.append(f"{suite}/{loop.name}: meta.json's hot_loop differs from the packager's")
expect(f"{rendered} TSVC and E2-B1 packages equal their packager's rendering", rendered > 0 and not drift,
       "; ".join(drift[:4]) + (f" (+{len(drift) - 4} more)" if len(drift) > 4 else ""))


# ---- 1d. a file a model reads is an ordinary code file (the author, 4 Oct 2026; packaging v5, v6) ------
# "the only thing we should do if we receive a benchmark, we have to make sure to remove the comments": no
# comment in any file of a clean package — the benchmark's own, data.h, main.c: a model can read all three —
# and nothing of the measurement in the benchmark's own file or in data.h: no `pb_` name, no harness include.
# v5: the repetition loop and its counter belong to main.c alone. v6: the repetition loop is the function's,
# as in TSVC — once, with TSVC's `dummy` call once after the loop under study, and never the harness's `R`.
print("1d. packaging v5, v6, v7: no comment in a file a model reads, nothing of the harness in the benchmark's file")
clean, dirty = 0, []
for meta_p in sorted(PREPARED.rglob("meta.json")):
    meta = json.loads(meta_p.read_text())
    editable = (meta.get("project") or {}).get("editable")
    if not editable:
        continue
    pkg = meta_p.parent
    for f in sorted(p for p in pkg.iterdir() if p.suffix in SOURCE_EXT):
        text = f.read_text()
        clean += 1
        if "/*" in text or "//" in text:
            dirty.append(f"{f.relative_to(PREPARED)}: a comment")
        if f.name in editable or f.name == "data.h":
            if re.search(r"\bpb_\w*|\bPB_\w*", text):
                dirty.append(f"{f.relative_to(PREPARED)}: a harness name")
            if re.search(r'#include\s+"[^"]*/', text):
                dirty.append(f"{f.relative_to(PREPARED)}: an include from outside the package")
        if f.name in editable and meta.get("generator_version") in (6, 7):
            # v7: where TSVC's own call hands `dummy` a number, the call keeps it (`dummy(a, b, c, d, e, dot);`)
            if (len(re.findall(r"for \(int nl = 0; nl < iterations; nl\+\+\)", text)) != 1
                    or len(re.findall(r"\bdummy\(a, b, c, d, e(?:, \w+)?\);", text)) != 1 or re.search(r"\bR\b", text)):
                dirty.append(f"{f.relative_to(PREPARED)}: not one repetition loop with one `dummy` call")
        elif f.name in editable and re.search(r"\bnl\b|\bR\b", text):
            dirty.append(f"{f.relative_to(PREPARED)}: the repetition loop")
    stray = sorted(p.name for p in pkg.iterdir() if p.name != "meta.json" and p.suffix not in SOURCE_EXT)
    if stray:
        dirty.append(f"{pkg.relative_to(PREPARED)}: files that are not sources ({', '.join(stray)})")
expect(f"{clean} files of v5, v6 and v7 packages are ordinary code files", clean > 0 and not dirty,
       "; ".join(dirty[:4]) + (f" (+{len(dirty) - 4} more)" if len(dirty) > 4 else ""))


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
    elif Damage.kind in ("harness_once", "harness_always"):
        # 3 Oct: a program that edits the measurement lines is redone by the runner
        (trial / "agent.log").write_text(f"call {Damage.calls}\n")
        edited = Damage.kind == "harness_always" or Damage.calls == 1
        return {"benchmark": bench, "kernel": bench_dir.name, "arm": arm, "model": model, "status": "ok",
                "scaffold": {"ok": not edited, "problems": ["protected line added: pb_mix(nl);"] if edited else [],
                             "applies": True},
                "verify": {"status": "ok"}}
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

# ---- 5. a harness edit is redone (3 Oct), every attempt kept outside benchmarks/ -------
for kind, calls, redos, final_edit in (("harness_once", 2, 1, False),
                                       ("harness_always", 1 + cli.HARNESS_EDIT_REDOS, cli.HARNESS_EDIT_REDOS, True)):
    Damage.kind, Damage.calls = kind, 0
    run("_test_harness_redo", "calib/vecsum", 1)
    recs = trial_records("_test_harness_redo")
    t = json.loads(recs[0].read_text()) if len(recs) == 1 else {}
    kept = sorted((RUNS / "_test_harness_redo" / "_harness_edit").rglob("trial.json"))
    expect(f"{kind}: {calls} attempt(s), one trial record", Damage.calls == calls and len(recs) == 1,
           f"{Damage.calls} calls, {len(recs)} records")
    expect(f"{kind}: {redos} redo(s) recorded and kept", len(t.get("harness_edit_redos") or []) == redos
           and len(kept) == redos and all((k.parent / "agent.log").exists() for k in kept), str(t.get("harness_edit_redos")))
    expect(f"{kind}: final outcome", (t.get("outcome") == "SCAFFOLD_MODIFIED") == final_edit, str(t.get("outcome")))
    expect(f"{kind}: the final attempt's own files in the trial", (recs[0].parent / "agent.log").exists()
           and (recs[0].parent / "agent.log").read_text() == f"call {calls}\n")
Damage.kind = "none"
shutil.rmtree(RUNS / "_test_harness_redo", ignore_errors=True)

print(f"\n{'ALL PASS' if not fails else f'{fails} FAILURE(S)'}")
sys.exit(1 if fails else 0)
