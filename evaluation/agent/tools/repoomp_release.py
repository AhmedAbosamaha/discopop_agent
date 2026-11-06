#!/usr/bin/env python3
"""E11 part 2 — RepoOMP's RELEASED pipeline (RepoOMP_Simplified, commit 45a1b9f, `benchmarks/RepoOMP`) on one of
our packaged kernels, one trial. Not the paper's full system: the release's README lists what it lacks (full MAP,
Bear, tree-sitter, transitive confidence propagation, blocker merging, High/Middle/Low routing). Named
`repoomp_release` everywhere, apart from part 1's `repoomp_published` programs.

The release's own driver (`Method/run_all.py`, `npb_pipeline`) is wired to NPB's and BOTS's paths. This follows
its control flow step by step on a package and calls the release's OWN code for every step that decides anything:

  step                          release code used                         what is ours
  0  dependence analysis        dependency_analysis/dependency_analyzer.py include dirs: the package, the harness
  0b hot functions              run_all.npb_hot_heuristic (uftrace-free)   —
  0c sequential baseline        —                                          build, check, time (below)
  1  rules                      run_all.rules_transform                    —
  2  accept rules               run_all's rule: checked AND faster         the check and the time
  2.5 model on the rules' file  primitive_adder.py --base, 3 attempts      include dirs; the model by the shim
  3  model on the original      primitive_adder.py, 3 attempts             (llm_transform's loop, mirrored)
  3b fallback                   the original when nothing passed           —
  final                         the fastest checked candidate that beats the sequential time, else the original

Ours, the same for every candidate: the build is the package's (clang-20 -O2 -fopenmp; the release builds NPB
at -O0); the CHECK is the full value dump (-DPB_FULL_DUMP) at the agent size, every value within 1e-8 relative of
the sequential program's (NPB's own verification tolerance; the release checks NPB's verdict); the TIME is the
best of `--runs` runs of the timed region at the timing size; threads `--threads` (the release's default is 4).
The release's comparison with its `_aaai.c` reference does not exist for our kernels (there is none) and is not
made. The model is reached through `claude_openai_shim.py` (REPOOMP_API_BASE). The final file goes to the harness
like any other candidate (`verify-source --label repoomp_release`); this tool's own verdict is only RepoOMP's.

    venv/bin/python evaluation/agent/tools/repoomp_release.py tsvc_c2/k23 --out RUN/tsvc_c2/k23/rep1 \
        --api-base http://127.0.0.1:18765/v1 --model claude-sonnet-4-5-20250929 --repoomp-python ~/repoomp_venv/bin/python
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
AGENT_DIR = HERE.parent
PREPARED = AGENT_DIR / "prepared"
REPOOMP = AGENT_DIR.parent / "benchmarks" / "RepoOMP"
METHOD = REPOOMP / "Method"
sys.path.insert(0, str(HERE))
import harness_include  # noqa: E402
HARNESS = harness_include.install()

NUM = re.compile(r"[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?|(?<![A-Za-z_])[-+]?(?:inf|nan)(?![A-Za-z_])", re.I)
REGION = re.compile(r"^DP_TIMED_REGION_SECONDS\s+([0-9.eE+-]+)\s*$", re.M)
TOL = 1e-8


def _sizes(bench: str) -> Tuple[str, str]:
    """(agent size, timing size) as the harness reads them (config/kernel_sizes.json)."""
    table = json.loads((AGENT_DIR / "config" / "kernel_sizes.json").read_text()).get("kernels", {})
    return "SMALL", str((table.get(bench) or {}).get("timing_size") or "SMALL")


def _sh(cmd: List[str], cwd: Optional[Path] = None, env: Optional[Dict[str, str]] = None,
        timeout: int = 600) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return 124, "", f"timeout after {timeout} s"


class Package:
    def __init__(self, bench: str, cc: str, threads: int, runs: int, work: Path):
        self.bench, self.cc, self.threads, self.runs, self.work = bench, cc, threads, runs, work
        self.dir = PREPARED / bench
        meta = json.loads((self.dir / "meta.json").read_text())
        proj = meta.get("project") or {}
        self.editable = (proj.get("editable") or [meta["file"]])[0]
        self.units: List[str] = list(proj.get("units") or [meta["file"]])
        self.includes: List[str] = list(proj.get("include_dirs") or ["."])
        self.cflags: List[str] = list(proj.get("cflags") or [])
        self.agent_size, self.timing_size = _sizes(bench)
        self.n = 0

    def build(self, src: Path, size: str, dump: bool) -> Tuple[Optional[Path], str]:
        self.n += 1
        d = self.work / f"build{self.n}"
        shutil.copytree(self.dir, d, ignore=shutil.ignore_patterns("meta.json", ".discopop"))
        shutil.copy2(src, d / self.editable)
        exe = d / "a.out"
        cmd = [self.cc, "-O2", "-fopenmp", f"-D{size}_DATASET", *(["-DPB_FULL_DUMP"] if dump else []),
               *[str(d / u) for u in self.units], *[f"-I{d / i}" for i in self.includes], *self.cflags,
               "-o", str(exe), "-lm"]
        rc, _o, err = _sh(cmd, cwd=d)
        return (exe if rc == 0 else None), err[-800:]

    def run(self, exe: Path) -> Tuple[int, str, str]:
        env = {**os.environ, "OMP_NUM_THREADS": str(self.threads)}
        return _sh([str(exe)], cwd=exe.parent, env=env, timeout=1800)


def _same(ref: str, out: str) -> Tuple[bool, str]:
    """Every value within TOL relative, everything else identical."""
    rs, os_ = NUM.split(ref), NUM.split(out)
    rn, on = NUM.findall(ref), NUM.findall(out)
    if rs != os_ or len(rn) != len(on):
        return False, "the output's text or number of values differs"
    worst = 0.0
    for a, b in zip(rn, on):
        fa, fb = float(a), float(b)
        if fa != fa or fb != fb:
            if not (fa != fa and fb != fb):
                return False, "nan in one output only"
            continue
        if fa == fb:
            continue
        err = abs(fa - fb) / max(abs(fa), abs(fb), 1e-300)
        worst = max(worst, err)
    return worst <= TOL, f"max relative difference {worst:.3g}"


def check_and_time(pkg: Package, src: Path, ref_dump: Optional[str]) -> Dict[str, Any]:
    """RepoOMP's 'verify and time', on the package: the full dump at the agent size against the sequential
    program's, then the best of `runs` timed regions at the timing size."""
    rec: Dict[str, Any] = {}
    exe, err = pkg.build(src, pkg.agent_size, dump=True)
    if exe is None:
        return {"built": False, "error": err}
    rc, out, err = pkg.run(exe)
    rec.update(built=True, dump_rc=rc)
    if rc != 0:
        return {**rec, "verified": False, "error": err[-400:]}
    if ref_dump is not None:
        ok, why = _same(ref_dump, out)
        rec.update(verified=ok, check=why)
        if not ok:
            return rec
    else:
        rec.update(verified=True, dump=out)
    exe, err = pkg.build(src, pkg.timing_size, dump=False)
    if exe is None:
        return {**rec, "time": None, "error": err}
    times = []
    for _ in range(pkg.runs):
        rc, out, err = pkg.run(exe)
        m = [float(x) for x in REGION.findall(out + "\n" + err)]
        if rc != 0 or not m:
            return {**rec, "time": None, "error": f"timed run failed ({rc}): {err[-300:]}"}
        times.append(sum(m))
    rec.update(time=min(times), times=times)
    return rec


def model_transform(pkg: Package, source: Path, out_dir: Path, name: str, dep_json: Path, hot_json: Path,
                    base: bool, env: Dict[str, str], py: str, log: List[Dict[str, Any]]) -> Optional[Path]:
    """`run_all.llm_transform`, mirrored: primitive_adder.py up to three times, the first run that accepts at
    least one function is kept. Only the include directories differ (the package and the harness, not NPB's)."""
    candidate = out_dir / f"{name}{'_llm_on_rules' if base else '_llm'}.c"
    best: Optional[Path] = None
    best_accepted = 0
    for attempt in range(3):
        cmd = [py, str(METHOD / "primitive_addition" / "primitive_adder.py"), "--src", str(source), "--dep",
               str(dep_json), "--hot", str(hot_json), "--out", str(candidate),
               "--include-dirs", ",".join([str(pkg.work / "src"), str(HARNESS)])]
        if base:
            cmd += ["--base", str(source)]
        t0 = time.time()
        rc, out, err = _sh(cmd, cwd=METHOD, env=env, timeout=900)
        status_file = Path(str(candidate) + ".status.json")
        try:
            status = json.loads(status_file.read_text())
        except (OSError, json.JSONDecodeError):
            status = {}
        n_acc = sum(1 for b in status.get("batches", []) if b.get("accepted"))
        log.append({"step": "model_on_rules" if base else "model", "attempt": attempt + 1, "rc": rc,
                    "accepted_batches": n_acc, "seconds": round(time.time() - t0, 1),
                    # primitive_adder's own verdict per function (accepted, or the reason it rejected the model's
                    # candidate); its status file is overwritten by the next attempt, so it is kept here (6 Nov)
                    "status": status,
                    "stderr_tail": err[-600:], "stdout_tail": out[-600:]})
        if rc != 0 or not candidate.exists():
            continue
        if n_acc > best_accepted:
            best_accepted = n_acc
            best = Path(str(candidate) + f".run{attempt}")
            candidate.rename(best)
        if best_accepted > 0:
            break
    if best is not None and best.exists():
        best.rename(candidate)
    return candidate if candidate.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("benchmark", help="a packaged kernel, e.g. tsvc_c2/k23")
    ap.add_argument("--out", type=Path, required=True, help="the trial directory")
    ap.add_argument("--api-base", default="", help="the shim's URL; empty = no model (the rules path only)")
    ap.add_argument("--model", default="claude-sonnet-4-5-20250929")
    ap.add_argument("--repoomp-python", default=sys.executable, help="a python with `openai` (primitive_adder.py)")
    ap.add_argument("--cc", default="clang-20")
    ap.add_argument("--threads", type=int, default=12)
    ap.add_argument("--runs", type=int, default=5, help="timed runs per candidate, best taken (the release's 5)")
    a = ap.parse_args()

    out = a.out.resolve()
    if out.exists():
        sys.exit(f"{out} exists — one trial per directory")
    work = out / "work"
    (work / "src").mkdir(parents=True)
    pkg = Package(a.benchmark, a.cc, a.threads, a.runs, work)
    name = Path(pkg.editable).stem
    for f in pkg.dir.iterdir():
        if f.is_file() and f.name != "meta.json":
            shutil.copy2(f, work / "src" / f.name)
    source = work / "src" / pkg.editable
    shutil.copytree(pkg.dir, out / "original", ignore=shutil.ignore_patterns("meta.json", ".discopop"))

    # RepoOMP's tools call `clang`, `gcc` and `python3` by name; the server has clang-20 only.
    tools_bin = work / "bin"
    tools_bin.mkdir()
    if not shutil.which("clang"):
        os.symlink(shutil.which(a.cc) or a.cc, tools_bin / "clang")
    env = {**os.environ, "PATH": f"{tools_bin}{os.pathsep}{os.environ.get('PATH', '')}",
           "REPOOMP_API_KEY": "local" if a.api_base else "", "REPOOMP_API_BASE": a.api_base,
           "REPOOMP_MODEL": a.model, "OMP_NUM_THREADS": str(a.threads)}
    os.environ.update({k: v for k, v in env.items() if k in ("PATH", "REPOOMP_API_KEY", "REPOOMP_API_BASE",
                                                            "REPOOMP_MODEL")})
    sys.path.insert(0, str(METHOD))
    import run_all  # type: ignore[import-not-found]   # RepoOMP's own module: rules_transform, npb_hot_heuristic

    log: List[Dict[str, Any]] = []
    res: Dict[str, Any] = {"benchmark": a.benchmark, "tool": "repoomp_release.py", "repoomp_commit": "45a1b9f",
                           "model_id": a.model if a.api_base else None, "threads": a.threads, "runs": a.runs,
                           "agent_size": pkg.agent_size, "timing_size": pkg.timing_size, "cc": a.cc,
                           "started_at": time.strftime("%Y-%m-%dT%H:%M:%S")}

    # step 0: dependence analysis (the release's analyzer, the package's include dirs)
    dep_json = work / f"{name}_dep.json"
    rc, o, e = _sh(["python3", str(METHOD / "dependency_analysis" / "dependency_analyzer.py"), "--src", str(source),
                    "--out", str(dep_json), f"--include=-I{work / 'src'}", f"--include=-I{HARNESS}",
                    "--flag=-fopenmp"], cwd=METHOD, env=env, timeout=300)
    res["dep_analyzed"] = rc == 0 and dep_json.exists()
    log.append({"step": "dependence_analysis", "rc": rc, "stdout_tail": o[-600:], "stderr_tail": e[-600:]})
    hot_json = run_all.npb_hot_heuristic(dep_json, work, name, source) if res["dep_analyzed"] else None
    if res["dep_analyzed"]:
        res["dep_summary"] = json.loads(dep_json.read_text()).get("summary")

    # step 0b: the sequential program
    serial = check_and_time(pkg, source, None)
    ref_dump = serial.pop("dump", None)
    res["serial"] = serial
    if not serial.get("verified") or serial.get("time") is None:
        res["error"] = "the sequential program did not build or run"
        return _finish(out, source, None, "none", res, log)
    serial_time = float(serial["time"])
    opt: Optional[Path] = None
    opt_method, opt_time = "none", None

    # step 1-2: rules, accepted if checked and faster
    rules_ok, cand, _audit, n_changes, rules_err = run_all.rules_transform(source, work, name,
                                                                           dep_json=dep_json if res["dep_analyzed"] else None)
    res["rules_changes"] = n_changes
    rules_verified = False
    if rules_ok and cand and cand.exists() and n_changes > 0 and _sha(cand) != _sha(source):
        r = check_and_time(pkg, cand, ref_dump)
        res["rules"] = r
        rules_verified = bool(r.get("verified"))
        if rules_verified and r.get("time") is not None and r["time"] < serial_time:
            opt, opt_method, opt_time = cand, "rules", r["time"]
    else:
        res["rules"] = {"skipped": rules_err or "rules_no_match"}

    if a.api_base:
        # step 2.5: the model on the rules' file, only when that file passed the check
        if rules_verified and cand is not None:
            lr = model_transform(pkg, cand, work, name, dep_json, hot_json or work / "none.json", True, env,
                                 a.repoomp_python, log)
            if lr is not None:
                r = check_and_time(pkg, lr, ref_dump)
                # primitive_adder writes its input back when it accepts no function (no hotspot, or every candidate
                # rejected): then nothing was proposed, whatever the check and the timing say (6 Nov)
                r["candidate_equals_source"] = _sha(lr) == _sha(cand)
                res["model_on_rules"] = r
                if r.get("verified") and r.get("time") is not None and (opt_time is None or r["time"] < opt_time):
                    opt, opt_method, opt_time = lr, "rules+model", r["time"]
        # step 3: the model on the original, always
        lc = model_transform(pkg, source, work, name, dep_json, hot_json or work / "none.json", False, env,
                             a.repoomp_python, log)
        if lc is not None:
            lc_fixed = work / f"{name}_llm_fixed.c"
            lc_fixed.write_text(run_all._fix_thread_report(lc.read_text(errors="replace")))
            r = check_and_time(pkg, lc_fixed, ref_dump)
            r["candidate_equals_source"] = _sha(lc_fixed) == _sha(source)
            res["model"] = r
            if r.get("verified") and r.get("time") is not None and r["time"] < serial_time \
                    and (opt_time is None or r["time"] < opt_time):
                opt, opt_method, opt_time = lc_fixed, "model", r["time"]
        else:
            res["model"] = {"skipped": "no candidate from the model"}
    res["opt_method"], res["opt_time"] = opt_method, opt_time
    for step in ("model_on_rules", "model"):
        att = [{k: x.get(k) for k in ("attempt", "rc", "accepted_batches", "status")} for x in log if x.get("step") == step]
        if att:
            res[f"{step}_attempts"] = att
    res["speedup_own_check"] = (serial_time / opt_time) if opt_time else None
    return _finish(out, source, opt, opt_method, res, log)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _finish(out: Path, source: Path, opt: Optional[Path], method: str, res: Dict[str, Any],
            log: List[Dict[str, Any]]) -> int:
    """final/ = the package with RepoOMP's accepted file, or the original (step 3b: nothing passed)."""
    final = out / "final"
    shutil.copytree(out / "original", final)
    # RepoOMP's own small records leave work/ (which the fetch skips): its dependence and hotspot files, the rules'
    # file and audit, the model's candidate functions and prompts, primitive_adder's last status (6 Nov)
    work, ev = out / "work", out / "evidence"
    if work.is_dir():
        ev.mkdir(exist_ok=True)
        for f in sorted(work.iterdir()):
            if f.is_file() and f.suffix in (".json", ".c", ".txt"):
                shutil.copy2(f, ev / f.name)
    editable = Path(source).name
    if opt is not None:
        shutil.copy2(opt, final / editable)
    # from the content: the release may "accept" a model file byte-equal to the original on timing noise (6 Nov)
    res["final_changed"] = opt is not None and _sha(opt) != _sha(source)
    res["finished_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    (out / "repoomp_result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
    (out / "repoomp_log.json").write_text(json.dumps(log, indent=1, default=str) + "\n")
    print(f"{res['benchmark']}: {method}" + (f", {res['speedup_own_check']:.2f}× by its own check"
                                              if res.get("speedup_own_check") else ""), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
