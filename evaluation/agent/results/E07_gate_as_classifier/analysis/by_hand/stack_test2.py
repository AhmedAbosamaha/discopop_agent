"""By-hand positive test for E7's accepted-but-crashing rewrites (run on the server, piped on stdin, nothing left behind):
build each program at its verification size exactly as the harness's verification does, run it once under the default
stack limit and once with the limit raised to unlimited, and print the return codes."""
import json, resource, shutil, subprocess, sys, tempfile, time
from pathlib import Path
EVAL = Path.cwd()
sys.path.insert(0, str(EVAL / "agent/tools")); sys.path.insert(0, str(EVAL / "shared")); sys.path.insert(0, str(EVAL.parent))
import cli  # noqa: E402
C = EVAL / "agent/results/E07_gate_as_classifier/corpus/a1"
WANT = [("tsvc_c2/s244", "3f7bcc2a0b4fc7fa"), ("tsvc_c2/s244", "37798c09a53933ce")]
print("soft stack limit:", resource.getrlimit(resource.RLIMIT_STACK))
def unlimited():
    resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
for bench, h16 in WANT:
    bench_dir = cli._prepared_benchmarks()[bench]
    src_name = cli._source_name(bench_dir)
    prog = C / "programs" / bench / h16 / src_name
    vsize, _ = cli._verify_size("per_kernel", bench)
    proj = cli._project_of(bench_dir)
    compiler = cli._find_tool(None, "AGENT_CC", cli._CC_CANDIDATES, "clang")
    with tempfile.TemporaryDirectory(prefix="e7_hand_") as tmp:
        work = Path(tmp)
        cli._copy_tree(bench_dir, work / "p")
        shutil.copy2(prog, work / "p" / src_name)
        inputs = ([str(work / "p" / u) for u in proj["units"]] + [f"-I{work / 'p' / d}" for d in proj.get("include_dirs") or []]
                  + list(proj.get("cflags") or []))
        for opt in ("-O2", "-O0"):
            cmd = [compiler, opt, f"-D{vsize}_DATASET", *inputs, "-o", str(work / "t"), *list(proj.get("ldflags") or []),
                   *cli._toolchain_flags(True, True)]
            b = subprocess.run(cmd, capture_output=True, text=True, cwd=work, timeout=900)
            if b.returncode != 0:
                print(bench, h16, opt, "BUILD FAILED", b.stderr[-300:]); continue
            res = []
            for label, pre in (("default stack", None), ("unlimited stack", unlimited)):
                t0 = time.time()
                r = subprocess.run([str(work / "t")], capture_output=True, text=True, cwd=work, timeout=900, preexec_fn=pre,
                                   env={**__import__("os").environ, "OMP_NUM_THREADS": "6"})
                res.append(f"{label}: rc {r.returncode} in {time.time() - t0:.1f} s")
            print(f"{bench} {h16[:8]} at {vsize}, {opt}: " + " | ".join(res), flush=True)
