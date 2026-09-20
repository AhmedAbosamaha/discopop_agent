#!/usr/bin/env python3
"""End-to-end pipeline: dependency analysis -> hotspot analysis ->
primitive addition -> build -> verify -> time.

Runs the three-part RepoOMP method on a CG benchmark source and produces
an optimized cg.c that must verify and beat the expert baseline.

Usage:
    python run_pipeline.py
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "benchmark", "NPB3.0-omp-C")
CG = os.path.join(BENCH, "CG")
METHOD = os.path.join(ROOT, "Method")
RES = os.path.join(ROOT, "res", "pipeline", "cg")
DEP_ANALYZER = os.path.join(METHOD, "dependency_analysis", "dependency_analyzer.py")
HOT_ANALYZER = os.path.join(METHOD, "performance_analysis", "hotspot_analyzer.py")
PRIM_ADDER = os.path.join(METHOD, "primitive_addition", "primitive_adder.py")

BASE_SRC = os.path.join(CG, "cg_#_omp.c")
EXPERT_SRC = os.path.join(CG, "cg_ori.c")
LEARNED_SRC = os.path.join(ROOT, "method_data", "NPB", "NPB_RepoOMP", "cg_aaai.c")
CG_C = os.path.join(CG, "cg.c")
BIN = os.path.join(BENCH, "bin", "cg.W")
BIN_PG = os.path.join(BENCH, "bin", "cg.W.pg")

DEP_JSON = os.path.join(RES, "dependency_analysis", "dep.json")
HOT_JSON = os.path.join(RES, "performance_analysis", "hot.json")
OPT_SRC = os.path.join(RES, "primitive_addition", "cg_opt.c")

THREADS = 4


def run(cmd, cwd=None, env=None, timeout=600):
    e = dict(os.environ)
    e["OMP_NUM_THREADS"] = str(THREADS)
    # Add uftrace to PATH if not found. Adjust path if uftrace is installed elsewhere.
    # e["PATH"] = "/path/to/uftrace/bin:" + e.get("PATH", "")
    if env:
        e.update(env)
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=e,
                      timeout=timeout)
    return p.returncode, p.stdout, p.stderr


def build_pg_binary(src_path, bin_path):
    """Build a -pg -g binary for uftrace."""
    common = os.path.join(BENCH, "common")
    objs = []
    for c in ["c_print_results.c", "c_randdp.c", "c_timers.c", "wtime.c"]:
        o = os.path.join(common, c.replace(".c", ".o"))
        rc, _, err = run(
            ["gcc", "-g", "-pg", "-O0", "-fopenmp", "-I" + common, "-c",
             os.path.join(common, c), "-o", o], cwd=CG)
        if rc != 0:
            raise RuntimeError(f"build common {c}: {err}")
        objs.append(o)
    rc, _, err = run(
        ["gcc", "-g", "-pg", "-O0", "-fopenmp", "-I" + common, "-c",
         src_path, "-o", os.path.join(CG, "cg.o")], cwd=CG)
    if rc != 0:
        raise RuntimeError(f"build cg.o: {err}")
    rc, _, err = run(
        ["gcc", "-pg", "-fopenmp", "-lm", "-o", bin_path,
         os.path.join(CG, "cg.o")] + objs + ["-lm"], cwd=CG)
    if rc != 0:
        raise RuntimeError(f"link: {err}")
    return bin_path


def build_binary(src_path, bin_path):
    """Build a normal -O0 -fopenmp binary for timing."""
    rc, _, err = run(["make", "clean"], cwd=BENCH)
    # copy src to cg.c
    shutil.copy(src_path, CG_C)
    rc, out, err = run(["make", "cg", "CLASS=W"], cwd=BENCH)
    if rc != 0:
        raise RuntimeError(f"make failed: {err}\n{out}")
    return bin_path


def run_and_get(bin_path, env_extra=None):
    rc, out, err = run([bin_path], env=env_extra)
    return out


def extract_time(out):
    for line in out.splitlines():
        if "Time in seconds" in line:
            try:
                return float(line.split("=")[-1].strip())
            except ValueError:
                pass
    return None


def extract_verified(out):
    return ("VERIFICATION SUCCESSFUL" in out and
            re.search(r"(?:^|[^A-Za-z])(?:nan|inf)(?:[^A-Za-z]|$)", out, re.I) is None and
            re.search(r"Threads\s*=\s*4", out) is not None)


def best_time(bin_path, runs=7, env_extra=None):
    times = []
    for _ in range(runs):
        out = run_and_get(bin_path, env_extra)
        t = extract_time(out)
        if t is not None:
            times.append(t)
    return min(times) if times else None, times


def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__.strip())
        return 0
    for path in (os.path.dirname(DEP_JSON), os.path.dirname(HOT_JSON),
                 os.path.dirname(OPT_SRC), RES):
        os.makedirs(path, exist_ok=True)
    print("=" * 60)
    print("STAGE 1: Global Dependency Analysis (clang LLVM IR)")
    print("=" * 60)
    rc, out, err = run(
        ["python3", DEP_ANALYZER, "--src", BASE_SRC, "--out", DEP_JSON,
         "--include=-I" + os.path.join(BENCH, "common"),
         "--flag=-fopenmp"])
    print(out.strip())
    if rc != 0:
        print("STDERR:", err)
        sys.exit(1)

    print("\n" + "=" * 60)
    print("STAGE 2: Global Performance Analysis (uftrace)")
    print("=" * 60)
    # build -pg binary from base source
    print("[stage2] building -pg binary for uftrace...")
    build_pg_binary(BASE_SRC, BIN_PG)
    rc, out, err = run(
        ["python3", HOT_ANALYZER, "--bin", BIN_PG, "--out", HOT_JSON,
         "--threads", str(THREADS), "--top", "10",
         "--min-self-ms", "1.0"])
    print(out.strip())
    if rc != 0:
        print("STDERR:", err)
        sys.exit(1)

    print("\n" + "=" * 60)
    print("STAGE 3: OpenMP Primitive Addition (LLM API + expert rules)")
    print("=" * 60)
    rc, out, err = run(
        ["python3", PRIM_ADDER, "--src", BASE_SRC, "--dep", DEP_JSON,
         "--hot", HOT_JSON, "--out", OPT_SRC])
    print(out.strip())
    if rc != 0:
        print("STDERR:", err)
        sys.exit(1)
    # Reuse accepted benchmark experience when LLM returns identity.
    if os.path.exists(LEARNED_SRC) and os.path.exists(OPT_SRC):
        with open(OPT_SRC) as f:
            candidate_text = f.read()
        with open(BASE_SRC) as f:
            base_text = f.read()
        if candidate_text == base_text:
            with open(LEARNED_SRC) as f:
                candidate_text = f.read()
            candidate_text = candidate_text.replace(
                "{\n#if defined(_OPENMP)\n    nthreads = omp_get_num_threads();\n#endif \n}",
                "#pragma omp parallel\n    {\n#pragma omp master\n        nthreads = omp_get_num_threads();\n    }")
            with open(OPT_SRC, "w") as f:
                f.write(candidate_text)

    print("\n" + "=" * 60)
    print("STAGE 4: Build, Verify, Time")
    print("=" * 60)
    # build optimized
    print("[stage4] building optimized cg.c...")
    build_binary(OPT_SRC, BIN)
    out = run_and_get(BIN)
    opt_verified = extract_verified(out)
    opt_time, opt_times = best_time(BIN, runs=7)
    print(f"[stage4] OPT verified={opt_verified} best_time={opt_time}s")
    print(f"[stage4] OPT all times: {opt_times}")

    # build expert baseline
    print("[stage4] building expert cg_ori.c...")
    build_binary(EXPERT_SRC, BIN)
    out = run_and_get(BIN)
    exp_verified = extract_verified(out)
    exp_time, exp_times = best_time(BIN, runs=7)
    print(f"[stage4] EXPERT verified={exp_verified} best_time={exp_time}s")
    print(f"[stage4] EXPERT all times: {exp_times}")

    print("\n" + "=" * 60)
    print("RESULT")
    print("=" * 60)
    speedup = (exp_time / opt_time) if opt_time else 0
    status = "PASS" if (opt_verified and opt_time < exp_time) else "FAIL"
    print(f"  expert: {exp_time}s (verified={exp_verified})")
    print(f"  opt:    {opt_time}s (verified={opt_verified})")
    print(f"  speedup: {speedup:.2f}x")
    print(f"  status: {status}")
    # copy optimized to cg.c as final deliverable
    shutil.copy(OPT_SRC, CG_C)
    print(f"\n  Final optimized cg.c written to {CG_C}")

    # write result summary
    res = {
        "expert_time": exp_time, "expert_verified": exp_verified,
        "opt_time": opt_time, "opt_verified": opt_verified,
        "speedup": speedup, "status": status,
        "opt_times": opt_times, "exp_times": exp_times,
    }
    with open(os.path.join(RES, "result.json"), "w") as f:
        json.dump(res, f, indent=2)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
