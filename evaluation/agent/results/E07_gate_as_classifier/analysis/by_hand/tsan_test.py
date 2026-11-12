"""By-hand test of why the judge's race check (J2) reports nothing on programs where the gate's sanitizer reports a race
in every run (run on the server, piped on stdin, nothing left behind).  J2 and the gate's check differ in two things:
the size (J2: the verification size; the gate: the package's own small size) and the optimisation level of the
sanitized build (J2: the harness's -O2; the gate: -O1).  Each program is built in the four combinations and run
twice at 12 threads in the gate's ThreadSanitizer environment (archer, halt_on_error=1).
usage (from evaluation/, on the server):  python - < tsan_test.py"""
import json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path
EVAL = Path.cwd()
sys.path.insert(0, str(EVAL / "agent/tools")); sys.path.insert(0, str(EVAL / "shared")); sys.path.insert(0, str(EVAL.parent))
import cli  # noqa: E402
from discopop_agent.gate.toolchain import _tsan_env  # noqa: E402
R = EVAL / "agent/results/E07_gate_as_classifier/corpus"
WANT = [("a2", "polybench/adi", 3), ("a2", "polybench/seidel-2d", 3), ("a1", "tsvc_c2/s341", 16)]
for corpus, bench, idx in WANT:
    c = json.loads((R / corpus / "corpus.json").read_text())
    h = next(k for k, v in c["programs"].items() if v["benchmark"] == bench and v["index"] == idx)
    prog = R / corpus / c["programs"][h]["path"]
    bench_dir = cli._prepared_benchmarks()[bench]
    src_name = cli._source_name(bench_dir)
    is_c = Path(src_name).suffix == ".c"
    compiler = (cli._find_tool(None, "AGENT_CC", cli._CC_CANDIDATES, "clang") if is_c
                else cli._find_tool(None, "AGENT_CXX", cli._CXX_CANDIDATES, "clang++"))
    vsize, _ = cli._verify_size("per_kernel", bench)
    proj = cli._project_of(bench_dir)
    with tempfile.TemporaryDirectory(prefix="e7_hand_") as tmp:
        work = Path(tmp)
        if proj is None:
            shutil.copy2(prog, work / src_name)
            inputs, tail = [str(work / src_name)], []
        else:
            cli._copy_tree(bench_dir, work / "p")
            shutil.copy2(prog, work / "p" / src_name)
            inputs = ([str(work / "p" / u) for u in proj["units"]] + [f"-I{work / 'p' / d}" for d in proj.get("include_dirs") or []]
                      + list(proj.get("cflags") or []))
            tail = list(proj.get("ldflags") or [])
        for size in (None, vsize):
            for opt in ("-O1", "-O2"):
                cmd = [compiler, opt, *([f"-D{size}_DATASET"] if size else []), "-fsanitize=thread", "-g", *inputs, "-o", str(work / "t"),
                       *tail, *cli._toolchain_flags(True, is_c)]
                b = subprocess.run(cmd, capture_output=True, text=True, cwd=work, timeout=900)
                if b.returncode != 0:
                    print(bench, idx, size, opt, "BUILD FAILED", b.stderr[-300:], flush=True); continue
                env = _tsan_env(); env["OMP_NUM_THREADS"] = "12"
                res = []
                for _ in range(2):
                    t0 = time.time()
                    try:
                        r = subprocess.run([str(work / "t")], capture_output=True, text=True, cwd=work, env=env, timeout=900)
                        race = "WARNING: ThreadSanitizer" in r.stderr or "DATA RACE" in r.stderr
                        res.append(f"{'RACE' if race else 'clean'} (rc {r.returncode}, {time.time() - t0:.1f} s)")
                    except subprocess.TimeoutExpired:
                        res.append("timed out (900 s)")
                print(f"{corpus} {bench} #{idx}  size {size or 'package default'}  {opt}:  " + " | ".join(res), flush=True)
print("archer:", os.path.basename(_tsan_env().get("OMP_TOOL_LIBRARIES", "none")), " TSAN_OPTIONS:", _tsan_env().get("TSAN_OPTIONS"))
