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

import sys
from pathlib import Path


def _cxx_wrapper() -> str:
    return str(Path(sys.executable).parent / "discopop_cxx")


def _explorer_cmd() -> str:
    return str(Path(sys.executable).parent / "discopop_explorer")


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
