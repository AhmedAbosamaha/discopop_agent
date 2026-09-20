#!/usr/bin/env python3
"""Greedy validation search over deterministic OpenMP pragma candidates."""
import argparse
import json
import subprocess
from pathlib import Path

from rule_transformer import transform


def run_verify(repo, candidate, name, cls, threads, out):
    cmd = ["python3", "Method/verify.py", "--source", str(candidate),
           "--benchmark-root", "benchmark/NPB3.0-omp-C", "--name", name,
           "--class", cls, "--threads", str(threads), "--runs", "1",
           "--out", str(out)]
    return subprocess.run(cmd, cwd=repo, capture_output=True, text=True).returncode == 0


def search(source, repo, name, cls, threads, out, audit_out):
    source = Path(source).resolve()
    repo = Path(repo).resolve()
    work = Path(out).resolve().parent / (name + ".pragma-search")
    work.mkdir(parents=True, exist_ok=True)
    all_candidate = work / "all.c"
    rule_audit = work / "all.audit.json"
    transform(str(source), str(all_candidate), str(rule_audit))
    source_lines = source.read_text(errors="replace").splitlines()
    candidate_lines = all_candidate.read_text(errors="replace").splitlines()
    pragmas = [line for line in candidate_lines if line.lstrip().startswith("#pragma omp")]
    accepted = []
    current = source_lines[:]
    attempts = []
    for index, pragma in enumerate(pragmas):
        target_header = None
        for pos, line in enumerate(candidate_lines):
            if line == pragma and pos + 1 < len(candidate_lines):
                target_header = candidate_lines[pos + 1].strip()
                candidate_lines[pos] = ""
                break
        if not target_header:
            continue
        insert_at = next((i for i, line in enumerate(current) if line.strip() == target_header), None)
        if insert_at is None:
            attempts.append({"index": index, "pragma": pragma.strip(), "accepted": False, "reason": "header-not-unique"})
            continue
        trial_lines = current[:insert_at] + [pragma] + current[insert_at:]
        trial = work / f"trial-{index}.c"
        verify_out = work / f"trial-{index}.verify.json"
        trial.write_text("\n".join(trial_lines) + "\n")
        ok = run_verify(repo, trial, name, cls, threads, verify_out)
        attempts.append({"index": index, "pragma": pragma.strip(), "line": insert_at + 1, "accepted": ok, "verification": str(verify_out)})
        if ok:
            current = trial_lines
            accepted.append(pragma.strip())
    Path(out).write_text("\n".join(current) + "\n")
    audit = {"schema": "repoomp.pragma-search.v1", "source": str(source), "output": str(Path(out).resolve()),
             "candidate_count": len(pragmas), "accepted_count": len(accepted), "accepted": accepted, "attempts": attempts}
    Path(audit_out).write_text(json.dumps(audit, indent=2))
    return audit


def main():
    ap = argparse.ArgumentParser(description="Search safe pragma subset by workload validation")
    ap.add_argument("--source", required=True)
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--name", required=True)
    ap.add_argument("--class", dest="cls", default="S")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--out", required=True)
    ap.add_argument("--audit", required=True)
    args = ap.parse_args()
    result = search(args.source, args.repo, args.name, args.cls, args.threads, args.out, args.audit)
    print(f"[search] candidates={result['candidate_count']} accepted={result['accepted_count']}")


if __name__ == "__main__":
    main()
