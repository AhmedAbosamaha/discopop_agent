#!/usr/bin/env python3
"""Run reproducible NPB and BOTS reference checks.

This harness never edits benchmark sources. NPB checks use the existing Makefile
with temporary source backup. BOTS checks use configured binaries and the
project's run scripts, recording missing mappings as failures.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from exemplar_transformer import retrieve as exemplar_retrieve
from rule_transformer import transform as rule_transform
from reduction_transformer import transform as reduction_transform

NPB = ("bt", "cg", "ep", "ft", "is", "lu", "mg", "sp")
BOTS = ("alignment", "fft", "floorplan", "health", "nqueens", "sort", "sparselu", "strassen")


def run(cmd, cwd, env=None, timeout=900):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)


def npb_one(root, ref, cls, threads, runs, variant="aaai"):
    name = ref.stem.split("_")[0]
    bench = root / name.upper(); target = bench / f"{name}.c"
    backup = target.with_suffix(".c.repoomp-backup")
    result = {"suite": "NPB", "name": name, "reference": str(ref), "variant": variant, "class": cls, "threads": threads}
    shutil.copy2(target, backup)
    try:
        shutil.copy2(ref, target)
        # Some historical IS references omit declarations supplied by the
        # current NPB header. Add header only in temporary working copy.
        if name == "is":
            original = target.read_text(errors="replace")
            declarations = ('void timer_clear(int);\nvoid timer_start(int);\n'
                            'void timer_stop(int);\ndouble timer_read(int);\n'
                            'void c_print_results(char *, char, int, int, int, int, int, double, double, char *, int, char *, char *, char *, char *, char *, char *, char *, char *, char *);\n')
            original = re.sub(r"^main\( argc, argv \)", "int main( argc, argv )", original, count=1, flags=re.M)
            target.write_text(declarations + original)
        clean = run(["make", "clean"], root)
        build = run(["make", name, f"CLASS={cls}"], root)
        result["compile"] = build.returncode == 0
        if not result["compile"]:
            result["error"] = build.stderr[-2000:]; return result
        exe = root / "bin" / f"{name}.{cls}"
        env = dict(os.environ); env["OMP_NUM_THREADS"] = str(threads)
        times = []; verified = []
        for _ in range(runs):
            p = run([str(exe)], root, env)
            verification_string = ("VERIFICATION SUCCESSFUL" in p.stdout) or re.search(r"Verification\s*=\s*SUCCESSFUL", p.stdout) is not None
            nonfinite = bool(re.search(r"(?:^|[^A-Za-z])[-+]?nan(?:[^A-Za-z]|$)", p.stdout, re.I))
            thread_match = re.search(r"Threads\s*=\s*(\d+)", p.stdout)
            reported_threads = int(thread_match.group(1)) if thread_match else None
            thread_ok = (
                reported_threads is None
                or reported_threads == threads
                or variant in ("expert", "serial")
            )
            verified.append(verification_string and not nonfinite and thread_ok)
            m = re.search(r"Time in seconds\s*=\s*([0-9.eE+-]+)", p.stdout)
            if m: times.append(float(m.group(1)))
        result.update({"verified": all(verified), "verification_runs": verified, "times": times, "best_time": min(times) if times and all(verified) else None,
                      "accepted": bool(build.returncode == 0 and all(verified) and times)})
        if not result["verified"]:
            result["error"] = "workload verification failed in one or more runs"
        return result
    finally:
        shutil.copy2(backup, target); backup.unlink()


BOTS_RUN = {
    "alignment": ("for-omp-tasks", "prot.20.aa"),
    "fft": ("omp-tasks", "1048576"),
    "floorplan": ("omp-tasks", "input.5"),
    "health": ("omp-tasks", "test.input"),
    "nqueens": ("omp-tasks", "10"),
    "sort": ("omp-tasks", "1048576"),
    "sparselu": ("for-omp-tasks", "10x10"),
    "strassen": ("omp-tasks", "128"),
}


BOTS_SOURCE = {
    "alignment": "omp-tasks/alignment/alignment_for/alignment.c",
    "fft": "omp-tasks/fft/fft.c",
    "floorplan": "omp-tasks/floorplan/floorplan.c",
    "health": "omp-tasks/health/health.c",
    "nqueens": "omp-tasks/nqueens/nqueens.c",
    "sort": "omp-tasks/sort/sort.c",
    "sparselu": "omp-tasks/sparselu/sparselu_for/sparselu.c",
    "strassen": "omp-tasks/strassen/strassen.c",
}


def bots_one(root, ref, threads, runs, variant="aaai"):
    app = ref.stem.split("_")[0]
    version, input_value = BOTS_RUN[app]
    result = {"suite": "BOTS", "name": app, "reference": str(ref), "variant": variant, "threads": threads, "version": version, "input": input_value,
              "source_condition": "temporary source replacement"}
    target = root / BOTS_SOURCE[app]
    if variant == "current":
        ref = target
    elif variant == "serial":
        serial_target = root / "serial" / app
        serial_files = list(serial_target.glob("*.c"))
        if serial_files:
            ref = serial_files[0]
        else:
            result.update({"compile": False, "error": "serial source not found"})
            return result
    if not target.exists():
        result.update({"compile": False, "error": f"source target not found: {target}"})
        return result
    backup = target.with_suffix(target.suffix + ".repoomp-backup")
    build_dir = target.parent
    shutil.copy2(target, backup)
    try:
        if Path(ref).resolve() != target.resolve():
            shutil.copy2(ref, target)
            # copy2 preserves old timestamps, which can make make reuse stale objects.
            now = time.time() + 1
            os.utime(target, (now, now))
        installed_hash = __import__("hashlib").sha256(target.read_bytes()).hexdigest()
        reference_hash = __import__("hashlib").sha256(Path(ref).read_bytes()).hexdigest()
        result["installed_source_sha256"] = installed_hash
        result["reference_source_sha256"] = reference_hash
        result["source_identity_match"] = installed_hash == reference_hash
        if not result["source_identity_match"]:
            result.update({"compile": False, "error": "installed source hash mismatch"})
            return result
        clean = run(["make", "clean"], build_dir, timeout=900)
        build = run(["make"], build_dir, timeout=900)
        result["compile"] = build.returncode == 0
        result["build_returncode"] = build.returncode
        if not result["compile"]:
            result["error"] = (build.stderr or build.stdout)[-2000:]
            return result
        script = root / "run" / f"run-{app}.sh"
        times = []
        sequential_times = []
        verification_runs = []
        returncodes = []
        last = None
        for _ in range(runs):
            last = run([str(script), "-l", "gcc", "-v", version, "-c", str(threads), "-check", "-i", input_value], root, timeout=900)
            returncodes.append(last.returncode)
            verification_runs.append(re.search(r"Verification\s*=\s*successful", last.stdout, re.I) is not None)
            m = re.search(r"Time Program\s*=\s*([0-9.eE+-]+)", last.stdout)
            s = re.search(r"Time Sequential\s*=\s*([0-9.eE+-]+)", last.stdout)
            if m: times.append(float(m.group(1)))
            if s: sequential_times.append(float(s.group(1)))
        result["returncode"] = max(returncodes, default=1)
        result["verified"] = all(verification_runs)
        result["verification_runs"] = verification_runs
        result["times"] = times
        result["program_time"] = min(times) if times and result["verified"] else None
        result["sequential_time"] = min(sequential_times) if sequential_times else None
        result["accepted"] = bool(result["compile"] and result["verified"] and result["program_time"] is not None)
        if result["returncode"] or not result["verified"]:
            result["error"] = (last.stderr or last.stdout)[-2000:] if last else "runner did not execute"
        return result
    finally:
        shutil.copy2(backup, target)
        backup.unlink()
        # Restore executable state too. Matrix must not leave reference binary.
        run(["make", "clean"], build_dir, timeout=900)
        run(["make"], build_dir, timeout=900)


def generated_npb_one(root, source, cls, threads, runs, out_dir, repo, generator):
    name = source.stem.split("_")[0]
    candidate = out_dir / "NPB" / f"{name}_candidate.c"
    audit = candidate.with_suffix(".audit.json")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    if generator == "exemplar":
        exemplar_retrieve(repo, "npb", name, source, candidate, audit)
    elif generator == "reduction":
        reduction_transform(str(source), str(candidate), str(audit))
    else:
        rule_transform(str(source), str(candidate), str(audit))
    result = npb_one(root, candidate, cls, threads, runs, "generated")
    result["generator"] = generator
    result["audit"] = str(audit)
    provenance = json.loads(audit.read_text())
    expected_schema = {
        "exemplar": "repoomp.exemplar-transform.v1",
        "rules": "repoomp.rule-transform.v2",
        "reduction": "repoomp.reduction-transform.v1",
    }[generator]
    result["generator_provenance_valid"] = (
        provenance.get("schema") == expected_schema
        and provenance.get("generated_from_rules") == (generator != "exemplar")
    )
    if not result["generator_provenance_valid"]:
        result["accepted"] = False
        result["error"] = "generator provenance mismatch"
    if generator == "exemplar":
        result["source_identity_parity"] = provenance["output_sha256"] == provenance["exemplar_sha256"]
    return result


def bots_serial_one(root, app, threads, runs):
    input_value = BOTS_RUN[app][1]
    build_dir = root / "serial" / app
    result = {"suite": "BOTS", "name": app, "variant": "serial", "reference": str(build_dir),
              "threads": threads, "version": "serial", "input": input_value,
              "source_condition": "native BOTS serial build"}
    clean = run(["make", "clean"], build_dir, timeout=900)
    build = run(["make"], build_dir, timeout=900)
    result["compile"] = build.returncode == 0
    if not result["compile"]:
        result["error"] = (build.stderr or build.stdout)[-2000:]
        return result
    script = root / "run" / f"run-{app}.sh"
    times = []; verification = []; last = None
    for _ in range(runs):
        last = run([str(script), "-l", "gcc", "-v", "serial", "-c", str(threads), "-check", "-i", input_value], root, timeout=900)
        verification.append(bool(re.search(r"Verification\s*=\s*successful", last.stdout, re.I) or re.search(r"Verification\s*=\s*n/a", last.stdout, re.I)))
        m = re.search(r"Time Program\s*=\s*([0-9.eE+-]+)", last.stdout)
        if m: times.append(float(m.group(1)))
    result["verified"] = all(verification)
    result["verification_runs"] = verification
    result["times"] = times
    result["program_time"] = min(times) if times and result["verified"] else None
    result["accepted"] = bool(result["compile"] and result["verified"] and result["program_time"] is not None)
    if not result["verified"]:
        result["error"] = (last.stderr or last.stdout)[-2000:] if last else "runner did not execute"
    return result


def generated_bots_one(root, app, threads, runs, out_dir, repo, generator):
    source = root / BOTS_SOURCE[app]
    candidate = out_dir / "BOTS" / f"{app}_candidate.c"
    audit = candidate.with_suffix(".audit.json")
    candidate.parent.mkdir(parents=True, exist_ok=True)
    if generator == "exemplar":
        exemplar_retrieve(repo, "bots", app, source, candidate, audit)
    elif generator == "reduction":
        reduction_transform(str(source), str(candidate), str(audit))
    else:
        rule_transform(str(source), str(candidate), str(audit))
    result = bots_one(root, candidate, threads, runs, "generated")
    result["generator"] = generator
    result["audit"] = str(audit)
    provenance = json.loads(audit.read_text())
    expected_schema = {
        "exemplar": "repoomp.exemplar-transform.v1",
        "rules": "repoomp.rule-transform.v2",
        "reduction": "repoomp.reduction-transform.v1",
    }[generator]
    result["generator_provenance_valid"] = (
        provenance.get("schema") == expected_schema
        and provenance.get("generated_from_rules") == (generator != "exemplar")
    )
    if not result["generator_provenance_valid"]:
        result["accepted"] = False
        result["error"] = "generator provenance mismatch"
    if generator == "exemplar":
        result["source_identity_parity"] = provenance["output_sha256"] == provenance["exemplar_sha256"]
    return result


def main():
    ap = argparse.ArgumentParser(description="Run NPB and BOTS reference matrix")
    ap.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    ap.add_argument("--suite", choices=("npb", "bots", "all"), default="all")
    ap.add_argument("--class", dest="cls", default="W")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--out", required=True)
    ap.add_argument("--generated", action="store_true", help="also transform baseline sources and verify generated candidates")
    ap.add_argument("--generator", choices=("rules", "reduction", "exemplar"), default="rules")
    ap.add_argument("--reference-guided", action="store_true", help="run method_data references as an explicitly labelled upper bound")
    ap.add_argument("--thread-list", default=None, help="comma-separated thread counts, for example 1,4,16")
    args = ap.parse_args(); repo = Path(args.repo).resolve(); results = []
    out_path = Path(args.out).resolve()
    thread_list = [int(x) for x in args.thread_list.split(",") if x.strip()] if args.thread_list else [args.threads]
    if args.suite in ("npb", "all"):
        refs = repo / "method_data" / "NPB" / "NPB_RepoOMP"
        npb_root = repo / "benchmark" / "NPB3.0-omp-C"
        for name in NPB:
            variants = [("aaai", refs / f"{name}_aaai.c"), ("expert", npb_root / name.upper() / f"{name}_ori.c"), ("serial", npb_root / name.upper() / f"{name}_#_omp.c")]
            for variant, ref in variants:
                if not ref.exists():
                    results.append({"suite": "NPB", "name": name, "variant": variant, "reference": str(ref), "error": "reference missing", "compile": False})
                else:
                    for threads in thread_list:
                        result = npb_one(npb_root, ref, args.cls, threads, args.runs, variant)
                        if args.reference_guided and variant == "aaai":
                            result["upper_bound"] = True
                            result["source_condition"] = "method_data reference, not generated"
                        results.append(result)
            if args.generated:
                source = npb_root / name.upper() / f"{name}_#_omp.c"
                if source.exists():
                    for threads in thread_list:
                        results.append(generated_npb_one(npb_root, source, args.cls, threads, args.runs, out_path.parent, repo, args.generator))
                else:
                    results.append({"suite": "NPB", "name": name, "variant": "generated", "compile": False, "error": "baseline source missing"})
    if args.suite in ("bots", "all"):
        refs = repo / "method_data" / "BOTS" / "BOTS_RepoOMP"
        bots_root = repo / "benchmark" / "bots"
        for name in BOTS:
            ref = refs / f"{name}_aaai.c"
            for threads in thread_list:
                results.append({"suite": "BOTS", "name": name, "variant": "aaai", "reference": str(ref), "error": "reference missing", "compile": False} if not ref.exists() else bots_one(bots_root, ref, threads, args.runs, "aaai"))
                current_result = bots_one(bots_root, bots_root / BOTS_SOURCE[name], threads, args.runs, "current")
                current_result["source_condition"] = "benchmark expert source"
                current_result["variant"] = "expert"
                results.append(current_result)
                results.append(bots_serial_one(bots_root, name, threads, args.runs))
                if args.generated:
                    results.append(generated_bots_one(bots_root, name, threads, args.runs, out_path.parent, repo, args.generator))
    summary = {"schema": "repoomp.benchmark-matrix.v1", "results": results, "counts": {"total": len(results), "passed": sum(bool(x.get("compile") and x.get("verified", x.get("compile"))) for x in results)}}
    for item in results:
        if item.get("suite") == "BOTS" and item.get("program_time") and item.get("sequential_time"):
            item["speedup_vs_sequential"] = item["sequential_time"] / item["program_time"]
    Path(args.out).parent.mkdir(parents=True, exist_ok=True); Path(args.out).write_text(json.dumps(summary, indent=2)); print(json.dumps(summary["counts"]))
    raise SystemExit(0 if summary["counts"]["passed"] == summary["counts"]["total"] else 1)

if __name__ == "__main__": main()
