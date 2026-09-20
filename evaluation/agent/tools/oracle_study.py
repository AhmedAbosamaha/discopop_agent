#!/usr/bin/env python3
"""T0.3 — can the harness's correctness oracle see a wrong program?

The agent keeps EVERY candidate its gate judged — accepted or rejected, with the stage that
rejected it and its diff (`agent_patches/candidates.jsonl` + `candidates/NNNN.patch`). This
tool replays those candidates, from the runs archived under `agent/results/`, through the
harness's own verification (`cli.verify`: full value dump and digest against the original,
the perturbed input, repeats at fixed thread counts) and compares the oracle's verdict with
the gate's. No model is called.

For candidate k of a trial the program is rebuilt as the gate saw it: the trial's original
plus the patches of the candidates accepted before k, then patch k (`patch -p0 -F0`); if
that chain does not apply (a later revert changed the base), patch k is tried on the
original alone. Candidates rejected before a program existed (`clause`, `apply`, `compile`,
`openmp_compile`) have nothing to verify and are counted as such.

Reads: the oracle's sensitivity on programs the gate rejected for a RUNTIME reason (tsan,
schedules, correctness, dependences) — caught / not caught, and by which check — and its
agreement on programs the gate accepted (a BROKEN there is a gate false accept).

Output: `candidates.csv` (one row per candidate), `summary.json`, `run.log`, and one
verify record per replayed candidate under `replays/`.

    agent/tools/oracle_study.py --out agent/runs/t0_3_oracle [--results agent/results]
        [--runs a,b] [--threads 4] [--repeats 3] [--timeout 900]
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parents[1] / "shared")]
import cli  # noqa: E402

AGENT_DIR = HERE.parent
RUNTIME_STAGES = ("tsan", "schedules", "correctness", "dependences", "performance")
NO_PROGRAM_STAGES = ("clause", "apply", "compile", "openmp_compile")


def _relative_headers(patch: Path) -> str:
    """The diff with its `---`/`+++` paths made relative to the program root. The agent
    writes the path as it saw the file: bare (`2mm.c`), or absolute inside a trial's work
    copy (`…/work/IS/is.cpp` → `IS/is.cpp`) or a scratch directory (`…/prefix.c`)."""
    out = []
    for line in patch.read_text(errors="replace").splitlines(True):
        if line.startswith(("--- ", "+++ ")):
            tag, rest = line[:4], line[4:].rstrip("\n")
            path = rest.split("\t")[0]
            if "/work/" in path:
                path = path.split("/work/", 1)[1]
            elif path.startswith("/"):
                path = Path(path).name
            line = f"{tag}{path}\n"
        out.append(line)
    return "".join(out)


def _apply(patch: Path, root: Path) -> bool:
    """Apply a unified diff (paths made relative to `root`, no fuzz). False if it does not apply."""
    rel = root.parent / f"{patch.stem}_{root.name}.patch"
    rel.write_text(_relative_headers(patch))
    dry = subprocess.run(["patch", "-p0", "-F0", "-s", "--dry-run", "-i", str(rel)],
                         cwd=root, capture_output=True, text=True)
    if dry.returncode != 0:
        return False
    return subprocess.run(["patch", "-p0", "-F0", "-s", "--no-backup-if-mismatch", "-i", str(rel)],
                          cwd=root, capture_output=True, text=True).returncode == 0


def _stage_base(base: Path, dest: Path, src_name: str) -> None:
    """Copy the program (one file or a tree) into `dest`. A single file is staged under the
    benchmark's own file name, which is what the candidate diffs name (`--- seidel-2d.c`);
    a trial keeps it as `original.c`, an end-to-end run as `<name>.c.original`."""
    if base.is_dir():
        shutil.copytree(base, dest, ignore=shutil.ignore_patterns(".discopop", "a.out", "*.dSYM"))
    else:
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copy2(base, dest / src_name)


def _discover(results: Path, only_runs: Optional[List[str]]) -> List[dict]:
    """Every candidate of every archived trial, with what is needed to rebuild it."""
    out: List[dict] = []
    for index in sorted(results.rglob("candidates.jsonl")):
        parts = index.relative_to(results).parts
        run_id = parts[0]
        if only_runs and run_id not in only_runs:
            continue
        trial = index.parent.parent                       # .../rep1/agent_patches/candidates.jsonl
        bench: Optional[str] = None
        base: Optional[Path] = None
        if "benchmarks" in parts:
            i = parts.index("benchmarks")
            bench = f"{parts[i + 1]}/{parts[i + 2]}"
            singles = [p for p in trial.glob("original.*") if p.is_file()]
            base = trial / "original" if (trial / "original").is_dir() else (singles[0] if singles else None)
        else:
            # a rescued end-to-end run: <config>/<name>.c on a calibration program
            srcs = [p for p in trial.glob("*.c")] + [p for p in trial.glob("*.cpp")]
            orig = list((trial / "agent_patches").glob("*.original"))
            if srcs and (AGENT_DIR / "prepared" / "calib" / srcs[0].stem / "meta.json").exists():
                bench = f"calib/{srcs[0].stem}"
                base = orig[0] if orig else AGENT_DIR / "prepared" / "calib" / srcs[0].stem / srcs[0].name
        entries = [json.loads(l) for l in index.read_text().splitlines() if l.strip()]
        for e in entries:
            out.append({"run": run_id, "trial": str(trial.relative_to(results)), "benchmark": bench,
                        "base": base, "entry": e, "patch": index.parent / e["patch"],
                        "earlier_accepted": [index.parent / x["patch"] for x in entries[:e["n"]]
                                             if x.get("passed")]})
    return out


def replay(c: dict, out: Path, cc: str, cxx: str, threads: List[int], repeats: int,
           seed: Optional[str], timeout: float, log) -> dict:
    e = c["entry"]
    rec: dict = {"run": c["run"], "trial": c["trial"], "benchmark": c["benchmark"], "n": e["n"],
                 "phase": e.get("phase"), "region": e.get("region_id"), "gate_passed": e.get("passed"),
                 "gate_stage": e.get("stage"), "self_annotated": e.get("self_annotated"),
                 "pragmas": len(e.get("pragmas") or [])}
    if c["benchmark"] is None or c["base"] is None or not Path(c["base"]).exists():
        rec["replay"] = "no base program"
        return rec
    if e.get("stage") in NO_PROGRAM_STAGES and not e.get("passed"):
        rec["replay"] = "no program (rejected before a build)"
        return rec
    bench_dir = AGENT_DIR / "prepared" / c["benchmark"]
    if not (bench_dir / "meta.json").exists():
        rec["replay"] = "benchmark not packaged"
        return rec
    meta = json.loads((bench_dir / "meta.json").read_text())
    base = Path(c["base"])
    project = meta.get("project") if base.is_dir() else None
    src_name = meta["file"]
    ext = Path(src_name).suffix
    name = f"{c['run']}__{c['benchmark'].replace('/', '_')}__{Path(c['trial']).parts[-3]}_{Path(c['trial']).name}__cand{e['n']:04d}"
    tdir = out / "replays" / name
    shutil.rmtree(tdir, ignore_errors=True)
    tdir.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="t03_") as tmp:
        state = Path(tmp) / "state"
        _stage_base(base, state, src_name)
        chain_ok = True
        for p in c["earlier_accepted"]:
            if not _apply(p, state):
                chain_ok = False
                break
        applied_on = None
        if chain_ok and _apply(c["patch"], state):
            applied_on = "original + earlier accepted" if c["earlier_accepted"] else "original"
        else:
            shutil.rmtree(state)
            _stage_base(base, state, src_name)
            if _apply(c["patch"], state):
                applied_on = "original alone (chain did not apply)"
        rec["applied_on"] = applied_on
        if applied_on is None:
            rec["replay"] = "patch does not apply"
            return rec
        # lay the trial out as verify() expects it
        if project is not None:
            shutil.copytree(base, tdir / "original", ignore=shutil.ignore_patterns(".discopop", "a.out", "*.dSYM"))
            shutil.copytree(state, tdir / "final")
            final_text = cli._project_text(tdir / "final")
            orig_text = cli._project_text(tdir / "original")
        else:
            shutil.copy2(base, tdir / f"original{ext}")
            shutil.copy2(state / src_name, tdir / f"final{ext}")
            final_text = (tdir / f"final{ext}").read_text(errors="replace")
            orig_text = (tdir / f"original{ext}").read_text(errors="replace")
    rec["source_changed"] = final_text != orig_text
    rec["pragmas_added"] = cli._pragmas_added(orig_text, final_text)
    vsize, measurable = (cli._verify_size("per_kernel", c["benchmark"])
                         if cli._sizes_for(c["benchmark"]) else ("SMALL", False))   # calibration: SMALL
    rec["verify_size"] = vsize
    print(f"  {name}: gate {'PASS' if e.get('passed') else 'FAIL@' + str(e.get('stage'))}, "
          f"applied on {applied_on}, verifying at {vsize} …", file=log, flush=True)
    t0 = time.perf_counter()
    try:
        v = cli.verify(tdir, ext, cc, cxx, vsize, threads, repeats, seed, project=project)
    except subprocess.TimeoutExpired:
        v = {"status": "timeout"}
    v["speed_measurable"] = measurable
    rec["verify_s"] = round(time.perf_counter() - t0, 1)
    rec["verify"] = v
    rec["oracle_outcome"] = cli.classify({"verify": v, "source_changed": rec["source_changed"],
                                          "pragmas_in_final": rec["pragmas_added"], "kind": "replay"})
    rec["caught_by"] = _caught_by(v)
    rec["replay"] = "verified"
    (tdir / "trial.json").write_text(json.dumps(rec, indent=2, default=str) + "\n")
    return rec


def _caught_by(v: dict) -> List[str]:
    """Which of the oracle's checks flagged the program (empty = the oracle passed it)."""
    tol = cli.DIGEST_REL_TOL
    hits = []
    if v.get("status") != "ok":
        return [f"status:{v.get('status')}"]
    if (v.get("dump_max_rel_err") or 0) > tol or v.get("dump_max_rel_err") is None:
        hits.append("dump")
    if (v.get("dump_seeded_max_rel_err") or 0) > tol:
        hits.append("dump_seeded")
    if (v.get("digest_max_rel_err") or 0) > tol:
        hits.append("digest")
    if (v.get("digest_seeded_rel_err") or 0) > tol:
        hits.append("digest_seeded")
    if v.get("stable_at_fixed_threads") is False:
        hits.append("unstable_at_fixed_threads")
    return hits


def summarise(rows: List[dict]) -> dict:
    s: dict = {"candidates": len(rows), "replayed": 0, "not_replayed": {},
               "gate_rejected_runtime": {"n": 0, "caught": 0, "not_caught": 0, "by_stage": {}, "caught_by": {}},
               "gate_rejected_other": {"n": 0, "caught": 0, "not_caught": 0},
               "gate_accepted": {"n": 0, "oracle_ok": 0, "oracle_broken": 0, "broken": []}}
    for r in rows:
        if r.get("replay") != "verified":
            s["not_replayed"][r.get("replay", "?")] = s["not_replayed"].get(r.get("replay", "?"), 0) + 1
            continue
        s["replayed"] += 1
        broken = r["oracle_outcome"] in ("BROKEN", "VERIFY_FAILED")
        if r["gate_passed"]:
            g = s["gate_accepted"]
            g["n"] += 1
            g["oracle_broken" if broken else "oracle_ok"] += 1
            if broken:
                g["broken"].append({"run": r["run"], "trial": r["trial"], "n": r["n"],
                                    "outcome": r["oracle_outcome"], "caught_by": r["caught_by"]})
        elif r["gate_stage"] in RUNTIME_STAGES:
            g = s["gate_rejected_runtime"]
            g["n"] += 1
            g["caught" if broken else "not_caught"] += 1
            st = g["by_stage"].setdefault(r["gate_stage"], {"n": 0, "caught": 0})
            st["n"] += 1
            st["caught"] += int(broken)
            for hit in r["caught_by"]:
                g["caught_by"][hit] = g["caught_by"].get(hit, 0) + 1
        else:
            g = s["gate_rejected_other"]
            g["n"] += 1
            g["caught" if broken else "not_caught"] += 1
    return s


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--results", default=str(AGENT_DIR / "results"))
    ap.add_argument("--runs", default="", help="comma list of run ids (default: every archived run)")
    ap.add_argument("--threads", default="4", help="thread counts for the parallel runs")
    ap.add_argument("--repeats", type=int, default=3, help="runs per thread count (stability needs ≥ 2)")
    ap.add_argument("--check-seed", default="7")
    ap.add_argument("--timeout", type=float, default=900)
    ap.add_argument("--cc", default=None)
    ap.add_argument("--cxx", default=None)
    a = ap.parse_args()
    out = Path(a.out).resolve()          # verify() compiles from inside the trial directory
    out.mkdir(parents=True, exist_ok=True)
    log = open(out / "run.log", "a")
    cxx = cli._find_tool(a.cxx, "AGENT_CXX", cli._CXX_CANDIDATES, "clang++")
    cc = cli._find_tool(a.cc, "AGENT_CC", cli._CC_CANDIDATES, "clang")
    threads = [int(x) for x in a.threads.split(",") if x]
    started = time.strftime("%Y-%m-%dT%H:%M:%S")
    cands = _discover(Path(a.results), [r for r in a.runs.split(",") if r] or None)
    print(f"{len(cands)} candidates in {len({c['run'] for c in cands})} archived runs", flush=True)
    rows: List[dict] = []
    for c in cands:
        rec = replay(c, out, cc, cxx, threads, a.repeats, a.check_seed or None, a.timeout, log)
        rows.append(rec)
        tag = (f"oracle {rec['oracle_outcome']} {rec['caught_by'] or ''}" if rec.get("replay") == "verified"
               else rec.get("replay"))
        print(f"  {c['run']} {c['benchmark']} cand{c['entry']['n']:04d} gate "
              f"{'PASS' if c['entry'].get('passed') else 'FAIL@' + str(c['entry'].get('stage'))} → {tag}",
              flush=True)
        fields = ["run", "trial", "benchmark", "n", "phase", "region", "gate_passed", "gate_stage",
                  "self_annotated", "pragmas", "replay", "applied_on", "source_changed", "pragmas_added",
                  "verify_size", "oracle_outcome", "caught_by", "verify_s"]
        with open(out / "candidates.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            for r in rows:
                w.writerow({**r, "caught_by": " ".join(r.get("caught_by") or [])})
        (out / "summary.json").write_text(json.dumps({
            "study": "T0.3 oracle sensitivity on the gate's saved candidates", "host": platform.node(),
            "started": started, "finished": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "threads": threads, "repeats": a.repeats, "seed": a.check_seed, "cc": cc, "cxx": cxx,
            "results_dir": str(a.results), **summarise(rows)}, indent=2, default=str) + "\n")
    s = summarise(rows)
    print(json.dumps({k: v for k, v in s.items() if k != "gate_accepted"} | {"gate_accepted": {
        k: v for k, v in s["gate_accepted"].items() if k != "broken"}}, indent=1))
    print(f"wrote {out / 'candidates.csv'} and summary.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
