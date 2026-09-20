#!/usr/bin/env python3
"""Offline RepoOMP method entrypoint.

Runs evidence recovery, deterministic routing, and benchmark reference checks.
LLM transformation stays explicit and optional because it sends source off-host.
"""
import argparse
import json
import subprocess
from pathlib import Path


def run(cmd, cwd):
    return subprocess.run(cmd, cwd=cwd, check=False, text=True)


def main():
    ap = argparse.ArgumentParser(description="Run offline RepoOMP evidence and validation pipeline")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[1]))
    ap.add_argument("--suite", choices=("npb", "bots", "all"), default="all")
    ap.add_argument("--npb-class", default="A")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--out-dir", default="res/method_run")
    ap.add_argument("--transform-source", default=None)
    ap.add_argument("--verify-candidate", action="store_true")
    args = ap.parse_args()
    repo = Path(args.repo).resolve(); out = repo / args.out_dir
    out.mkdir(parents=True, exist_ok=True)
    steps = [
        (["python3", "Method/dependency_analysis/map_builder.py", "--root", "benchmark/NPB3.0-omp-C", "--out", str(out / "npb.map.json")], "npb_map"),
        (["python3", "Method/dependency_analysis/route_router.py", "--map", str(out / "npb.map.json"), "--out", str(out / "npb.routes.json")], "npb_routes"),
        (["python3", "Method/dependency_analysis/map_builder.py", "--root", "benchmark/bots", "--out", str(out / "bots.map.json")], "bots_map"),
        (["python3", "Method/dependency_analysis/route_router.py", "--map", str(out / "bots.map.json"), "--out", str(out / "bots.routes.json")], "bots_routes"),
        (["python3", "Method/primitive_addition/benchmark_matrix.py", "--suite", args.suite, "--class", args.npb_class, "--threads", str(args.threads), "--runs", str(args.runs), "--out", str(out / "benchmark.matrix.json")], "benchmark"),
    ]
    status = []
    for cmd, name in steps:
        p = run(cmd, repo); status.append({"name": name, "returncode": p.returncode})
        if p.returncode and name.endswith("map") or p.returncode and name.endswith("routes"):
            break
    if args.transform_source:
        candidate = out / "candidate.c"
        audit = out / "candidate.audit.json"
        map_path = out / "npb.map.json"
        routes_path = out / "npb.routes.json"
        p = run(["python3", "Method/primitive_addition/transformer.py", "--source", args.transform_source, "--map", str(map_path), "--routes", str(routes_path), "--out", str(candidate)], repo)
        status.append({"name": "transform", "returncode": p.returncode})
        if args.verify_candidate:
            verify_out = out / "candidate.verify.json"
            p = run(["python3", "Method/verify.py", "--source", str(candidate), "--benchmark-root", "benchmark/NPB3.0-omp-C", "--name", "cg", "--class", args.npb_class, "--threads", str(args.threads), "--runs", str(args.runs), "--out", str(verify_out)], repo)
            status.append({"name": "candidate_verify", "returncode": p.returncode})
    report = {"schema": "repoomp.offline-run.v1", "steps": status, "artifacts": str(out), "passed": all(x["returncode"] == 0 for x in status)}
    (out / "run.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return 0 if report["passed"] else 1

if __name__ == "__main__": raise SystemExit(main())
