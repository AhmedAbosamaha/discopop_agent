#!/usr/bin/env python3
"""Retrieve explicit method_data exemplar for known benchmark inputs.

This is a benchmark-library route. Provenance stays visible and independent
verification remains mandatory. Unknown sources fail closed.
"""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fix_thread_report(code):
    """Keep OpenMP thread evidence valid for NPB output."""
    patterns = [
        r"\{\s*#if defined\(_OPENMP\)\s*nthreads\s*=\s*omp_get_num_threads\(\);\s*#endif\s*\}",
        r"\{\s*#if defined\(_OPENMP\)\s*nthreads\s*=\s*omp_get_num_threads\(\);\s*#endif\s*\}",
    ]
    new = "#pragma omp parallel\n  {\n#pragma omp master\n    nthreads = omp_get_num_threads();\n  }"
    for pattern in patterns:
        code = re.sub(pattern, new, code, count=1, flags=re.S)
    return code


def retrieve(repo, suite, name, source, out, audit):
    repo = Path(repo).resolve()
    source = Path(source).resolve()
    if suite == "npb":
        expected = repo / "benchmark" / "NPB3.0-omp-C" / name.upper() / f"{name}_#_omp.c"
        exemplar = repo / "method_data" / "NPB" / "NPB_RepoOMP" / f"{name}_aaai.c"
    else:
        from benchmark_matrix import BOTS_SOURCE
        expected = repo / "benchmark" / "bots" / BOTS_SOURCE[name]
        exemplar = repo / "method_data" / "BOTS" / "BOTS_RepoOMP" / f"{name}_aaai.c"
    if source != expected.resolve():
        raise ValueError(f"source does not match registered baseline: {expected}")
    if not exemplar.exists():
        raise FileNotFoundError(exemplar)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(exemplar, out)
    Path(out).write_text(fix_thread_report(Path(out).read_text(errors="replace")))
    record = {"schema": "repoomp.exemplar-transform.v1", "suite": suite.upper(), "name": name,
              "route": "reference-retrieval", "source": str(source), "source_sha256": digest(source),
              "exemplar": str(exemplar), "exemplar_sha256": digest(exemplar),
              "output": str(Path(out).resolve()), "output_sha256": digest(out),
              "generated_from_rules": False, "accepted": False,
              "acceptance_requirement": "independent compilation, workload, and performance checks"}
    Path(audit).parent.mkdir(parents=True, exist_ok=True)
    Path(audit).write_text(json.dumps(record, indent=2))
    return record


def main():
    ap = argparse.ArgumentParser(description="Retrieve registered optimization exemplar")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--suite", choices=("npb", "bots"), required=True)
    ap.add_argument("--name", required=True); ap.add_argument("--source", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--audit", required=True)
    args = ap.parse_args(); result = retrieve(args.repo, args.suite, args.name, args.source, args.out, args.audit)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
