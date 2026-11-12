"""By-hand test: WHICH values of md's full dump differ between the original and DiscoPoP's directive on the particle
loop with `reduction(+:pe,ke)` (corpus A2, burkardt/md #8), which the gate refuses and the judge finds wrong (run on
the server, piped on stdin, nothing left behind).  The dump is md's energy table: per printed step the potential
energy, the kinetic energy and the relative energy error (potential + kinetic - e0) / e0.
usage (from evaluation/, on the server):  python - < md_dump_test.py"""
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
EVAL = Path.cwd()
sys.path.insert(0, str(EVAL / "agent/tools")); sys.path.insert(0, str(EVAL / "shared")); sys.path.insert(0, str(EVAL.parent))
import cli  # noqa: E402
R = EVAL / "agent/results/E07_gate_as_classifier/corpus/a2"
c = json.loads((R / "corpus.json").read_text())
bench = "burkardt/md"
bench_dir = cli._prepared_benchmarks()[bench]
src_name = cli._source_name(bench_dir)
compiler = cli._find_tool(None, "AGENT_CXX", cli._CXX_CANDIDATES, "clang++")
orig = next(R / v["path"] for v in c["programs"].values() if v["benchmark"] == bench and v["original"])
for idx in (8,):
    prog = next(R / v["path"] for v in c["programs"].values() if v["benchmark"] == bench and v["index"] == idx)
    with tempfile.TemporaryDirectory(prefix="e7_hand_") as tmp:
        work = Path(tmp)
        outs = {}
        for name, src, omp in (("orig", orig, False), ("cand", prog, True)):
            d = work / name; d.mkdir()
            shutil.copy2(src, d / src_name)
            cmd = [compiler, "-O2", "-DPB_FULL_DUMP", str(d / src_name), "-o", str(d / "t"), *cli._toolchain_flags(omp, False)]
            b = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
            if b.returncode != 0:
                sys.exit(f"{name} BUILD FAILED {b.stderr[-300:]}")
        for seed in ([], ["7"]):
            ref = subprocess.run([str(work / "orig" / "t"), *seed], capture_output=True, text=True, timeout=900).stdout.split()
            for threads in ("6", "12"):
                got = subprocess.run([str(work / "cand" / "t"), *seed], capture_output=True, text=True, timeout=900,
                                     env={**os.environ, "OMP_NUM_THREADS": threads}).stdout.split()
                print(f"md #{idx}, input {'perturbed (7)' if seed else 'shipped'}, {threads} threads: {len(ref)} values, {len(got)} printed")
                kinds = ["potential", "kinetic", "relative energy error"]
                worst = {k: 0.0 for k in kinds}
                over = {k: 0 for k in kinds}
                for i, (a, b_) in enumerate(zip(ref, got)):
                    x, y = float(a), float(b_)
                    rel = 0.0 if x == y else abs(x - y) / max(abs(x), abs(y))
                    k = kinds[i % 3]
                    worst[k] = max(worst[k], rel)
                    over[k] += rel > 1e-9
                    if rel > 1e-9 and over[k] <= 2:
                        print(f"   value {i} ({k}): original {a}  candidate {b_}  rel {rel:.2e}")
                print("   largest relative difference per column:", {k: f"{v:.2e}" for k, v in worst.items()},
                      " values over 1e-9 per column:", over, flush=True)
