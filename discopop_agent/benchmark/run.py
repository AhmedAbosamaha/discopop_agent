"""
Benchmark driver for the DiscoPoP agent.
----------------------------------------
Runs the WHOLE pipeline on each case in `cases/`, one isolated working copy per
case: profile with DiscoPoP -> run the agent -> independently re-measure what
the agent's final source is actually worth.

The last step matters most.  The agent reports its own verdicts, and a
benchmark that only echoed them would measure the agent's opinion of itself.
So after the agent finishes, the driver compiles the ORIGINAL source
sequentially and the FINAL source with -fopenmp, runs both, and compares wall
time and stdout itself.  "End-to-end speedup" in the report is that number, not
the agent's.

Usage (from the repository root):

    venv/bin/python -m discopop_agent.benchmark.run \\
        --provider claude-agent-sdk --model haiku --edit-mode direct

    venv/bin/python -m discopop_agent.benchmark.run --cases stencil_war prefix_sum
    venv/bin/python -m discopop_agent.benchmark.run --list
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from ..l3_llm import make_diff
from ..l4_validator import _find_clangpp, _macos_sysroot_flag

_HERE = Path(__file__).resolve().parent
_CASES = _HERE / "cases"
_MANIFEST = _HERE / "manifest.json"
_REPO = _HERE.parent.parent


# ---------------------------------------------------------------------------
# Result record
# ---------------------------------------------------------------------------

@dataclass
class CaseResult:
    name: str
    cause: str
    expect: str
    summary: str
    status: str = "pending"        # ok | failed | error | timeout | skipped
    detail: str = ""
    # what the agent did
    accepted: int = 0
    accepted_tiers: List[int] = field(default_factory=list)
    llm_calls: int = 0
    reverts: int = 0
    revert_reasons: List[str] = field(default_factory=list)
    agent_summary: str = ""
    source_changed: bool = False
    # independently re-measured
    baseline_ms: Optional[float] = None
    final_ms: Optional[float] = None
    speedup: Optional[float] = None
    output_matches: Optional[bool] = None
    pragmas_in_final: int = 0
    # cost
    profile_s: float = 0.0
    agent_s: float = 0.0
    total_s: float = 0.0
    workdir: str = ""


# ---------------------------------------------------------------------------
# Shell helpers
# ---------------------------------------------------------------------------

def _run(cmd: List[str], cwd: Path, timeout: int, env: Optional[dict] = None
         ) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, timeout=timeout, capture_output=True,
                          text=True, env=env)


def _venv_bin(name: str) -> str:
    return str(Path(sys.executable).parent / name)


def _agent_env() -> dict:
    """The agent must import from THIS checkout and find our venv's tools on
    PATH (the explorer shells out to a bare `discopop_patch_generator`)."""
    import os

    env = dict(os.environ)
    env["PATH"] = str(Path(sys.executable).parent) + os.pathsep + env.get("PATH", "")
    env["PYTHONPATH"] = str(_REPO) + os.pathsep + env.get("PYTHONPATH", "")
    return env


def _time_binary(binary: Path, cwd: Path, repeats: int = 3) -> "tuple[Optional[float], str]":
    """Best-of-N wall time in ms, plus stdout.  None if the program fails."""
    best = None
    out = ""
    for _ in range(repeats):
        t0 = time.perf_counter()
        try:
            r = subprocess.run([str(binary)], cwd=cwd, capture_output=True,
                               text=True, timeout=300)
        except subprocess.TimeoutExpired:
            return None, ""
        dt = (time.perf_counter() - t0) * 1e3
        if r.returncode != 0:
            return None, r.stdout
        out = r.stdout
        best = dt if best is None else min(best, dt)
    return best, out


def _compile(src: Path, out: Path, cwd: Path, clangpp: str, openmp: bool) -> bool:
    cmd = [clangpp, str(src), "-o", str(out), "-O2"] + _macos_sysroot_flag()
    if openmp:
        cmd.append("-fopenmp")
        libomp = Path("/usr/local/opt/libomp/lib")
        if libomp.exists():
            cmd += [f"-L{libomp}", f"-Wl,-rpath,{libomp}"]
    return _run(cmd, cwd, timeout=300).returncode == 0


# ---------------------------------------------------------------------------
# Phases
# ---------------------------------------------------------------------------

def _profile(work: Path, src_name: str, timeout: int) -> "tuple[bool, str]":
    """Instrument, run, and analyse — the state the agent expects to start from."""
    env = _agent_env()
    r = _run([_venv_bin("discopop_cxx"), src_name, "-o", "a.out"], work, timeout, env)
    if r.returncode != 0:
        return False, f"instrumentation failed:\n{r.stderr[-800:]}"
    r = _run(["./a.out"], work, timeout, env)
    if r.returncode != 0:
        return False, f"profiled run failed:\n{r.stderr[-800:]}"
    dp = work / ".discopop"
    if not dp.exists():
        return False, "no .discopop directory was produced"
    r = _run([_venv_bin("discopop_explorer")], dp, timeout, env)
    if r.returncode != 0:
        return False, f"explorer failed:\n{r.stderr[-800:]}"
    return True, ""


def _parse_agent_log(log: str) -> Dict[str, object]:
    """Pull the facts the report needs out of the agent's own output."""
    calls = log.count("] Calling ")
    reverts = log.count("— reverting")
    reasons = [
        line.split("[Tier-2] ", 1)[1].split(" — reverting")[0]
        for line in log.splitlines()
        if "— reverting" in line and "[Tier-2] " in line
    ]
    summary = ""
    for line in log.splitlines():
        if "SUMMARY:" in line:
            summary = line.split("SUMMARY:", 1)[1].strip()
    return {"llm_calls": calls, "reverts": reverts,
            "revert_reasons": reasons, "agent_summary": summary}


def _measure(work: Path, original: Path, final: Path, clangpp: str) -> Dict[str, object]:
    """Independent verdict: is the agent's final source correct, and is it faster?

    Baseline = the ORIGINAL source built sequentially (what the user had).
    Final    = the agent's source built with -fopenmp (what the user now has).
    """
    res: Dict[str, object] = {}
    base_bin, final_bin = work / "bench_base", work / "bench_final"
    if not _compile(original, base_bin, work, clangpp, openmp=False):
        res["detail"] = "baseline build failed"
        return res
    if not _compile(final, final_bin, work, clangpp, openmp=True):
        res["detail"] = "final build failed"
        return res
    base_ms, base_out = _time_binary(base_bin, work)
    final_ms, final_out = _time_binary(final_bin, work)
    res["baseline_ms"] = base_ms
    res["final_ms"] = final_ms
    res["output_matches"] = (base_out == final_out) if base_out else None
    if base_ms and final_ms:
        res["speedup"] = base_ms / final_ms
    res["pragmas_in_final"] = final.read_text().count("#pragma omp")
    return res


# ---------------------------------------------------------------------------
# One case
# ---------------------------------------------------------------------------

def run_case(case: dict, out_root: Path, agent_args: List[str], timeout: int,
             clangpp: str) -> CaseResult:
    name = case["name"]
    r = CaseResult(name=name, cause=case["cause"], expect=case["expect"],
                   summary=case["summary"])
    src_file = _CASES / f"{name}.cpp"
    if not src_file.exists():
        r.status, r.detail = "error", f"missing case source {src_file}"
        return r

    work = out_root / name
    work.mkdir(parents=True, exist_ok=True)
    r.workdir = str(work)
    original = work / f"{name}.cpp"
    shutil.copy2(src_file, original)
    pristine = original.read_text()
    (work / "original.cpp").write_text(pristine)

    t_start = time.perf_counter()
    print(f"\n{'='*72}\n  {name}  —  {case['cause']}\n{'='*72}")
    print(f"  {case['summary']}")

    # 1. profile
    print("  [1/3] profiling with DiscoPoP ...", flush=True)
    t0 = time.perf_counter()
    ok, detail = _profile(work, original.name, timeout)
    r.profile_s = time.perf_counter() - t0
    if not ok:
        r.status, r.detail = "error", detail
        r.total_s = time.perf_counter() - t_start
        print(f"        FAILED: {detail.splitlines()[0] if detail else ''}")
        return r
    print(f"        done in {r.profile_s:.1f}s")

    # 2. agent
    print("  [2/3] running the agent ...", flush=True)
    cmd = [sys.executable, "-m", "discopop_agent",
           "--source-file", original.name,
           "--discopop-dir", ".discopop"] + agent_args + list(case.get("agent_args", []))
    t0 = time.perf_counter()
    try:
        proc = _run(cmd, work, timeout, _agent_env())
        log = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        r.status, r.detail = "timeout", f"agent exceeded {timeout}s"
        r.agent_s = time.perf_counter() - t0
        r.total_s = time.perf_counter() - t_start
        print(f"        TIMEOUT after {timeout}s")
        return r
    r.agent_s = time.perf_counter() - t0
    (work / "agent.log").write_text(log)
    for k, v in _parse_agent_log(log).items():
        setattr(r, k, v)
    if proc.returncode != 0:
        r.status = "failed"
        r.detail = f"agent exited {proc.returncode}: {log.strip().splitlines()[-1] if log.strip() else ''}"
    print(f"        done in {r.agent_s:.1f}s  ({r.agent_summary or 'no summary'})")

    accepted_file = work / ".discopop" / "agent_patches" / "accepted.json"
    if accepted_file.exists():
        try:
            records = json.loads(accepted_file.read_text())
            r.accepted = len(records)
            r.accepted_tiers = [rec.get("tier", 0) for rec in records]
        except ValueError:
            pass

    # 3. independent re-measurement of the agent's final source
    print("  [3/3] re-measuring the result independently ...", flush=True)
    final_text = original.read_text()
    r.source_changed = final_text != pristine
    if r.source_changed:
        (work / "agent_changes.diff").write_text(
            make_diff(pristine, final_text, f"{name}.cpp")
        )
    for k, v in _measure(work, work / "original.cpp", original, clangpp).items():
        if hasattr(r, k):
            setattr(r, k, v)

    if r.status == "pending":
        r.status = "ok"
    r.total_s = time.perf_counter() - t_start
    spd = f"{r.speedup:.2f}x" if r.speedup else "n/a"
    match = {True: "identical", False: "DIFFERENT", None: "n/a"}[r.output_matches]
    print(f"        end-to-end {spd}  |  output {match}  |  "
          f"{r.pragmas_in_final} pragma(s) in final source")
    return r


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def _verdict(r: CaseResult) -> str:
    """One word for what actually happened, judged independently of the agent."""
    if r.status in ("error", "timeout"):
        return r.status.upper()
    if r.output_matches is False:
        return "BROKEN"          # the worst outcome: wrong results
    if r.pragmas_in_final == 0 and r.accepted == 0:
        return "no-change"
    if r.speedup is not None and r.speedup >= 1.1:
        return "FASTER"
    if r.pragmas_in_final > 0:
        return "parallel-not-faster"
    return "changed-not-parallel"


def write_report(results: List[CaseResult], out_root: Path, meta: dict) -> Path:
    lines = [
        "# DiscoPoP agent — benchmark report",
        "",
        f"- run: `{meta['started']}`",
        f"- model: `{meta['model']}` via `{meta['provider']}`, edit mode `{meta['edit_mode']}`",
        f"- agent args: `{' '.join(meta['agent_args']) or '(defaults)'}`",
        f"- total wall time: {meta['total_s']:.0f}s",
        "",
        "`Verdict` is measured by this driver, not reported by the agent: the "
        "original source built sequentially vs the agent's final source built "
        "with `-fopenmp`, same input, best of 3.",
        "",
        "| Case | Cause | Verdict | Speedup | Output | Accepted | LLM calls | Reverts | Profile | Agent |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for r in results:
        spd = f"{r.speedup:.2f}x" if r.speedup else "—"
        match = {True: "same", False: "**DIFFERENT**", None: "—"}[r.output_matches]
        tiers = "+".join(f"T{t}" for t in r.accepted_tiers) or "—"
        lines.append(
            f"| `{r.name}` | {r.cause} | {_verdict(r)} | {spd} | {match} | "
            f"{r.accepted} ({tiers}) | {r.llm_calls} | {r.reverts} | "
            f"{r.profile_s:.0f}s | {r.agent_s:.0f}s |"
        )

    lines += ["", "## Per case", ""]
    for r in results:
        lines += [
            f"### `{r.name}` — {_verdict(r)}",
            "",
            f"{r.summary}",
            "",
            f"- expected path: `{r.expect}`  |  status: `{r.status}`"
            + (f"  |  detail: {r.detail}" if r.detail else ""),
            f"- baseline {r.baseline_ms:.1f} ms → final {r.final_ms:.1f} ms"
            if r.baseline_ms and r.final_ms else "- timing unavailable",
            f"- agent summary: `{r.agent_summary or 'n/a'}`",
            f"- source changed: {'yes' if r.source_changed else 'no'}, "
            f"`#pragma omp` in final source: {r.pragmas_in_final}",
        ]
        if r.revert_reasons:
            lines.append("- reverted because:")
            for reason in r.revert_reasons:
                lines.append(f"    - {reason}")
        diff_file = Path(r.workdir) / "agent_changes.diff"
        if diff_file.exists():
            diff = diff_file.read_text().splitlines()
            shown = diff[:60]
            lines += ["", "<details><summary>what the agent changed</summary>", "",
                      "```diff", *shown]
            if len(diff) > 60:
                lines.append(f"... {len(diff) - 60} more lines")
            lines += ["```", "", "</details>"]
        lines += [f"- artifacts: `{r.workdir}` (agent.log, agent_changes.diff)", ""]

    report = out_root / "report.md"
    report.write_text("\n".join(lines) + "\n")
    (out_root / "results.json").write_text(
        json.dumps({"meta": meta, "results": [asdict(r) for r in results]}, indent=2)
    )
    return report


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    # A benchmark run takes minutes per case; block-buffered stdout would show
    # nothing until the end, which makes a long run indistinguishable from a
    # hung one.
    sys.stdout.reconfigure(line_buffering=True)  # type: ignore[union-attr]

    manifest = json.loads(_MANIFEST.read_text())
    names = [c["name"] for c in manifest["cases"]]

    p = argparse.ArgumentParser(
        description="Run the DiscoPoP agent over the benchmark cases and report "
                    "what it actually achieved."
    )
    p.add_argument("--cases", nargs="*", default=None,
                   help=f"subset to run (default: all). Available: {', '.join(names)}")
    p.add_argument("--list", action="store_true", help="list the cases and exit")
    p.add_argument("--provider", default="claude-agent-sdk")
    p.add_argument("--model", default="haiku")
    p.add_argument("--edit-mode", default="direct", choices=["diff", "function", "direct"])
    p.add_argument("--budget", type=int, default=3)
    p.add_argument("--restructure-depth", type=int, default=0)
    p.add_argument("--min-measured-speedup", type=float, default=1.1)
    # Every case ends with a small checksum loop, and DiscoPoP proposes patterns
    # for those too (sometimes wrongly — an unguarded `chk += ...` reads as a
    # Do-All).  They are two to three orders of magnitude lighter than the
    # kernel each case is about, so a workload floor keeps the agent — and the
    # benchmark's runtime — on the loop under test.
    p.add_argument("--min-workload", type=float, default=500000)
    p.add_argument("--timeout", type=int, default=1800,
                   help="per-phase timeout in seconds (default: 1800)")
    p.add_argument("--out", default=None,
                   help="output directory (default: benchmark/runs/<timestamp>)")
    p.add_argument("--verbose", action="store_true",
                   help="pass -v to the agent (full prompts and gate detail in agent.log)")
    a = p.parse_args()

    if a.list:
        for c in manifest["cases"]:
            extra = f"  [{' '.join(c['agent_args'])}]" if c.get("agent_args") else ""
            print(f"  {c['name']:<18} {c['cause']}{extra}\n      {c['summary']}")
        return 0

    selected = manifest["cases"]
    if a.cases:
        unknown = set(a.cases) - set(names)
        if unknown:
            print(f"unknown case(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
        selected = [c for c in manifest["cases"] if c["name"] in a.cases]

    clangpp = _find_clangpp()
    if clangpp is None:
        print("no supported clang++ found — see INSTALL.md", file=sys.stderr)
        return 2

    stamp = time.strftime("%Y%m%d-%H%M%S")
    out_root = Path(a.out) if a.out else _HERE / "runs" / stamp
    out_root.mkdir(parents=True, exist_ok=True)

    agent_args = [
        "--provider", a.provider, "--model", a.model,
        "--edit-mode", a.edit_mode, "--budget", str(a.budget),
        "--restructure-depth", str(a.restructure_depth),
        "--min-measured-speedup", str(a.min_measured_speedup),
        "--min-workload", str(a.min_workload),
    ] + (["-v"] if a.verbose else [])

    print(f"DiscoPoP agent benchmark — {len(selected)} case(s) → {out_root}")
    print(f"  {a.model} via {a.provider}, edit mode {a.edit_mode}, budget {a.budget}")

    t0 = time.perf_counter()
    results = []
    for case in selected:
        try:
            results.append(run_case(case, out_root, agent_args, a.timeout, clangpp))
        except KeyboardInterrupt:
            print("\ninterrupted — writing the report for what finished")
            break
    total_s = time.perf_counter() - t0

    meta = {
        "started": stamp, "provider": a.provider, "model": a.model,
        "edit_mode": a.edit_mode, "agent_args": agent_args, "total_s": total_s,
    }
    report = write_report(results, out_root, meta)

    print(f"\n{'='*72}")
    print(f"  {len(results)} case(s) in {total_s:.0f}s")
    for r in results:
        spd = f"{r.speedup:.2f}x" if r.speedup else "—"
        print(f"    {_verdict(r):<22} {r.name:<18} {spd:>7}")
    print(f"\n  report: {report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
