#!/usr/bin/env python3
"""Three-stage verification with candidate rollback records."""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from pathlib import Path


def _run(cmd, cwd=None, env=None, timeout=600):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""): h.update(chunk)
    return h.hexdigest()


def evaluate_batches(original_source, batches, compile_candidate, run_candidate,
                     baseline_runs, candidate_runs=5, audit_path=None):
    """Evaluate independent source batches with baseline threshold and rollback.

    Callbacks receive source text and return compile status or workload result.
    """
    def best(values):
        finite = [float(v) for v in values if v is not None and __import__('math').isfinite(float(v))]
        return min(finite) if finite else None
    baseline = list(baseline_runs(original_source))
    baseline_best = best(baseline)
    audit = {"baseline_runs": baseline, "baseline_best": baseline_best,
             "batches": [], "final_hash": hashlib.sha256(original_source.encode()).hexdigest()}
    accepted_source = original_source
    if baseline_best is None:
        audit["error"] = "baseline failure"
    else:
        for index, batch in enumerate(batches):
            candidate = batch(accepted_source) if callable(batch) else batch
            entry = {"batch": index, "candidate_hash": hashlib.sha256(candidate.encode()).hexdigest()}
            try:
                entry["compiled"] = bool(compile_candidate(candidate))
                if not entry["compiled"]:
                    entry["rollback_reason"] = "compile failure"
                    audit["batches"].append(entry); continue
                result = run_candidate(candidate, candidate_runs)
                if isinstance(result, dict) and result.get("verified") is False:
                    times = list(result.get("times", []))
                    candidate_best = None
                else:
                    times = list(result.get("times", result) if isinstance(result, dict) else result)
                    candidate_best = best(times)
                entry.update({"runs": times, "candidate_best": candidate_best,
                              "threshold": baseline_best, "accepted": candidate_best is not None and candidate_best <= baseline_best})
                if entry["accepted"]:
                    accepted_source = candidate
                else:
                    entry["rollback_reason"] = "correctness, nonfinite, or slower than baseline"
            except Exception as exc:
                entry.update({"accepted": False, "rollback_reason": str(exc)})
            audit["batches"].append(entry)
    audit["final_hash"] = hashlib.sha256(accepted_source.encode()).hexdigest()
    if audit_path:
        Path(audit_path).parent.mkdir(parents=True, exist_ok=True)
        Path(audit_path).write_text(json.dumps(audit, indent=2))
    return accepted_source, audit


def verify_npb(source, benchmark_root, name="cg", cls="W", threads=4, runs=5, workdir=None):
    root = Path(benchmark_root).resolve(); src = Path(source).resolve(); target = root / name.upper() / f"{name}.c"
    backup = target.with_suffix(target.suffix + ".repoomp-backup")
    record = {"schema": "repoomp.verification.v1", "workload": "NPB", "source": str(src), "stages": []}
    shutil.copy2(target, backup) if target.exists() else None
    try:
        shutil.copy2(src, target)
        clean = _run(["make", "clean"], cwd=root)
        build = _run(["make", name, f"CLASS={cls}"], cwd=root)
        compile_ok = build.returncode == 0
        record["stages"].append({"name": "compilation", "passed": compile_ok, "returncode": build.returncode, "stderr": build.stderr[-4000:]})
        if not compile_ok: return _finish(record, backup, target)
        exe = root / "bin" / f"{name}.{cls}"
        env = dict(os.environ); env["OMP_NUM_THREADS"] = str(threads)
        check = _run([str(exe)], cwd=root, env=env)
        verification_string = ("VERIFICATION SUCCESSFUL" in check.stdout) or re.search(r"Verification\s*=\s*SUCCESSFUL", check.stdout) is not None
        nonfinite = bool(re.search(r"(?:^|[^A-Za-z])[-+]?nan(?:[^A-Za-z]|$)", check.stdout, re.I))
        verified = verification_string and not nonfinite
        thread_match = re.search(r"Threads\s*=\s*(\d+)", check.stdout)
        reported_threads = int(thread_match.group(1)) if thread_match else None
        thread_mismatch = reported_threads is not None and reported_threads != threads
        verified = verified and not thread_mismatch
        record["stages"].append({"name": "workload", "passed": verified, "returncode": check.returncode, "verification_string": verification_string, "nonfinite_output": nonfinite, "reported_threads": reported_threads, "thread_mismatch": thread_mismatch, "stdout_tail": check.stdout[-4000:], "stderr_tail": check.stderr[-2000:]})
        if not verified: return _finish(record, backup, target)
        times = []
        for _ in range(runs):
            p = _run([str(exe)], cwd=root, env=env)
            for line in p.stdout.splitlines():
                if "Time in seconds" in line:
                    try: times.append(float(line.split("=")[-1].strip()))
                    except ValueError: pass
        perf_ok = bool(times)
        record["stages"].append({"name": "performance", "passed": perf_ok, "runs": times, "best_time": min(times) if times else None})
        record["passed"] = all(x["passed"] for x in record["stages"])
        return record
    finally:
        if backup.exists(): shutil.copy2(backup, target); backup.unlink()


def _finish(record, backup, target):
    record["passed"] = False
    return record


def main():
    ap = argparse.ArgumentParser(description="Verify NPB candidate and record rollback")
    ap.add_argument("--source", required=True); ap.add_argument("--benchmark-root", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--name", default="cg"); ap.add_argument("--class", dest="cls", default="W"); ap.add_argument("--threads", type=int, default=4); ap.add_argument("--runs", type=int, default=5)
    args = ap.parse_args(); result = verify_npb(args.source, args.benchmark_root, args.name, args.cls, args.threads, args.runs)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2)); print(f"[verify] wrote {args.out} passed={result.get('passed', False)}")
    raise SystemExit(0 if result.get("passed") else 1)

if __name__ == "__main__": main()
