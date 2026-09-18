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


def run_explorer(discopop_dir: Path, env: "dict[str, str] | None" = None
                 ) -> "subprocess.CompletedProcess[str]":
    """Run discopop_explorer in `discopop_dir`, retrying a crash on the same profile.

    The explorer is not deterministic on a fixed profile: run repeatedly on ONE
    profile it reports different task patterns each time and, on some programs,
    raises `IndexError: string index out of range` in
    `TaskGraph.recursive_assignment` on some attempts and not others (Rodinia
    `pathfinder`: 15 crashes in 20 attempts on one profile, so 20 attempts
    leave a 0.75^20 ≈ 0.3 % chance of losing the step). Fixing PYTHONHASHSEED does not change
    that. So a crash is a draw, not a verdict on the code: treating it as one
    reverted rewrites and discarded the dependence review for no reason. The
    profile is never touched between attempts; only the explorer's own partial
    output is cleared before a retry. Each retry is printed so a log shows it.
    Returns the last attempt's result.
    """
    import shutil

    r = subprocess.run([_explorer_cmd()], capture_output=True, text=True,
                       cwd=discopop_dir.resolve(), env=env if env is not None else _venv_env())
    attempt = 1
    while r.returncode != 0 and attempt < EXPLORER_ATTEMPTS:
        last = (r.stderr.strip().splitlines() or ["no output"])[-1][:120]
        print(f"      [explorer] attempt {attempt} failed ({last}) — retrying on the same profile")
        shutil.rmtree(discopop_dir / "explorer", ignore_errors=True)
        attempt += 1
        r = subprocess.run([_explorer_cmd()], capture_output=True, text=True,
                           cwd=discopop_dir.resolve(), env=env if env is not None else _venv_env())
    if attempt > 1:
        outcome = "succeeded" if r.returncode == 0 else "failed every time"
        print(f"      [explorer] {outcome} after {attempt} attempt(s)")
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
