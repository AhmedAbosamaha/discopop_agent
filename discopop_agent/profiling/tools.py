"""
Locating DiscoPoP's own tools, and the environment they need
--------------------------------------------------------------
The agent is normally launched as `venv/bin/python -m discopop_agent` WITHOUT
activating the venv, so `venv/bin` is not on PATH.  That matters because the
explorer shells out to a BARE `discopop_patch_generator`: without the venv's bin
prepended, PATH can resolve it to a stale global DiscoPoP that does not
understand newer pattern types and aborts the whole re-profile.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _cxx_wrapper() -> str:
    return str(Path(sys.executable).parent / "discopop_cxx")


def _wrapper_for(source: "str | Path") -> str:
    """DiscoPoP's compiler wrapper for `source`'s language: `discopop_cc` for C,
    `discopop_cxx` otherwise — instrumenting C through the C++ wrapper would
    compile it as C++ (see gate.toolchain.is_c_source)."""
    name = "discopop_cc" if Path(str(source)).suffix == ".c" else "discopop_cxx"
    return str(Path(sys.executable).parent / name)


class InstrumentedBuild:
    """How to build the program through one of DiscoPoP's compiler wrappers.

    `cmd` is run in `cwd` — which is also where DiscoPoP puts `.discopop` — and
    produces `binary`.  For a project the command compiles a generated unity unit
    (see project.py for why), which `cleanup()` removes again; the user's tree
    gains no file that outlives the build."""

    def __init__(self, source: "str | Path", binary_name: str = "a.out",
                 hotspot: bool = False) -> None:
        from .. import project as project_mod
        from ..gate.toolchain import link_flags_for

        proj = project_mod.active()
        self._unity: "Path | None" = None
        if proj is None:
            src = Path(source).resolve()
            is_c = src.suffix == ".c"
            self.cwd = src.parent
            self.binary = src.parent / binary_name
            body = [str(src), "-o", str(self.binary)]
            # The hotspot wrapper links libm for C itself being asked to; the
            # dependence wrapper takes the agent's usual link flags.
            tail = (["-lm"] if is_c else []) if hotspot else link_flags_for(src)
        else:
            is_c = not proj.is_cxx
            self.cwd = proj.root
            self.binary = proj.root / binary_name
            self._unity = proj.unity_path()
            self._unity.write_text(proj.unity_text())
            body = ([str(self._unity)] + proj.include_flags() + [f"-I{proj.root}"]
                    + list(proj.cflags) + ["-o", str(self.binary)])
            tail = list(proj.ldflags) + ((["-lm"] if is_c else []) if hotspot
                                         else link_flags_for(self._unity))
        stem = "discopop_hotspot_" if hotspot else "discopop_"
        wrapper = str(Path(sys.executable).parent / f"{stem}{'cc' if is_c else 'cxx'}")
        self.cmd = [wrapper] + body + tail

    def cleanup(self) -> None:
        if self._unity is not None:
            self._unity.unlink(missing_ok=True)


def _explorer_cmd() -> str:
    return str(Path(sys.executable).parent / "discopop_explorer")


# Attempts of discopop_explorer on one unchanged profile (see run_explorer).
EXPLORER_ATTEMPTS = 20


# A stalled explorer is a DRAW, like a crashed one (L5): on one unchanged profile the explorer
# sometimes finishes in seconds and sometimes spins for an hour in task detection — `s3112`
# took 5.8 s on the draw after the one that was still running at 80 minutes, and the rewritten
# `s211` stalled > 6 min on a Mac and finished in seconds on the next attempt.  Measured over
# 166 profile draws of the campaign's benchmarks: median 3.5 s, slowest legitimate run 33 s
# (Rodinia `hotspot`), 7 % of draws lost to a stall.  The limit is ~18x that slowest run, and
# 6x NPB-C CG's 99 s; a program whose explorer legitimately needs longer passes
# --explorer-timeout.  Until this existed the call had NO limit: a stall after a kept rewrite
# hung the trial until the harness killed the whole agent at its 90-minute limit — and it
# could only strike trials whose rewrite had been ACCEPTED, so the trials it removed were the
# agent's successes.
EXPLORER_STALL_S = 600.0
EXPLORER_STALL_ATTEMPTS = 5


def set_explorer_timeout(seconds: float) -> None:
    """Set from --explorer-timeout at start-up; 0 or less means no limit."""
    global EXPLORER_STALL_S
    EXPLORER_STALL_S = float(seconds)


def _explore_once(discopop_dir: Path, env: "dict[str, str]") -> "subprocess.CompletedProcess[str]":
    """One explorer attempt in its OWN process group, so a stall can be killed whole — the
    explorer shells out to the patch generator, which a plain kill would leave running."""
    import os
    import signal

    cmd = [_explorer_cmd()]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            cwd=discopop_dir.resolve(), env=env, start_new_session=True)
    try:
        out, err = proc.communicate(timeout=EXPLORER_STALL_S if EXPLORER_STALL_S > 0 else None)
        return subprocess.CompletedProcess(cmd, proc.returncode, out, err)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
        out, err = proc.communicate()
        return subprocess.CompletedProcess(
            cmd, -9, out or "", f"{err or ''}\nSTALLED: no result after {EXPLORER_STALL_S:.0f} s")


def run_explorer(discopop_dir: Path, env: "dict[str, str] | None" = None
                 ) -> "subprocess.CompletedProcess[str]":
    """Run discopop_explorer in `discopop_dir`, retrying a crash OR a stall on the same profile.

    The explorer is not deterministic on a fixed profile: run repeatedly on ONE
    profile it reports different task patterns each time and, on some programs,
    raises `IndexError: string index out of range` in
    `TaskGraph.recursive_assignment` on some attempts and not others (Rodinia
    `pathfinder`: 15 crashes in 20 attempts on one profile, so 20 attempts
    leave a 0.75^20 ≈ 0.3 % chance of losing the step). Fixing PYTHONHASHSEED does not change
    that. So a crash is a draw, not a verdict on the code: treating it as one
    reverted rewrites and discarded the dependence review for no reason. A STALL is a draw
    too (see EXPLORER_STALL_S above), limited separately: at most EXPLORER_STALL_ATTEMPTS
    stalls, since each costs the full limit. The profile is never touched between attempts;
    only the explorer's own partial output is cleared before a retry. Each retry is printed
    so a log shows it. Returns the last attempt's result.
    """
    import shutil

    use_env = env if env is not None else _venv_env()
    r = _explore_once(discopop_dir, use_env)
    attempt, stalls = 1, int(r.returncode == -9)
    while r.returncode != 0 and attempt < EXPLORER_ATTEMPTS and stalls < EXPLORER_STALL_ATTEMPTS:
        last = (r.stderr.strip().splitlines() or ["no output"])[-1][:120]
        what = "stalled" if r.returncode == -9 else "failed"
        print(f"      [explorer] attempt {attempt} {what} ({last}) — retrying on the same profile")
        shutil.rmtree(discopop_dir / "explorer", ignore_errors=True)
        attempt += 1
        r = _explore_once(discopop_dir, use_env)
        stalls += int(r.returncode == -9)
    if attempt > 1:
        outcome = "succeeded" if r.returncode == 0 else "failed every time"
        print(f"      [explorer] {outcome} after {attempt} attempt(s), {stalls} of them stalled")
    return r


def _venv_env() -> "dict[str, str]":
    """Environment with our venv's bin dir prepended to PATH.

    The agent is typically launched as `venv/bin/python -m discopop_agent`
    WITHOUT activating the venv, so `venv/bin` is not on PATH.  The explorer we
    spawn shells out to a BARE `discopop_patch_generator` (resolved via PATH);
    without this, PATH may resolve it to a stale/global DiscoPoP install
    (e.g. ~/.local/bin) that doesn't understand newer pattern types
    (`ValueError: Unknown task type: PARALLELREGION`) and exits 1, aborting the
    re-profile.  Prepending our venv's bin guarantees the matching tool wins.
    """
    import os

    env = dict(os.environ)
    venv_bin = str(Path(sys.executable).parent)
    env["PATH"] = venv_bin + os.pathsep + env.get("PATH", "")
    return env
