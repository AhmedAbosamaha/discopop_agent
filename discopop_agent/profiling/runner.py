"""
Producing DiscoPoP's data: the full re-profile, the fast refresh, and hotspots
-------------------------------------------------------------------------------
Three ways to get a profile, in descending cost:

  full        instrument -> run the instrumented binary -> explore.  The run
              scales with the workload (17x native on a 104M-operation kernel),
              and it is the only step that needs the program to execute.
  fast        compile only, then translate the PREVIOUS run's observed
              dependences onto the new instruction numbering.  Anything that
              cannot be translated with certainty is dropped, never guessed.
  hotspots    a separate instrumentation pass that measures how long each region
              takes.  Runs once, and is what lets candidates be ranked by time
              saved rather than by instruction count.
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Dict, List

from ..args import AgentArguments
from ..plan import impact as impact_mod
from . import fast_refresh
from ..gate.toolchain import _LLVM_LIBCXX
from .tools import _cxx_wrapper, _explorer_cmd, _venv_env


# Artifacts the instrumented RUN produces.  A fast refresh re-runs only the
# compile, which does not write these, so they are preserved across it and
# translated onto the new numbering instead.
_RUN_ARTIFACTS = (
    "dynamic_dependencies.txt",
    "loop_counter_output.txt",
    "reduction.txt",
    "memory_regions.txt",
)


def _measure_hotspots(args: AgentArguments, dp_dir: Path) -> "tuple[bool, str]":
    """Run DiscoPoP's hotspot detection once, unless it has already run.

    Separate from the dependence profile in every way: its own instrumentation
    pass, its own binary, its own output directory.  It answers a question the
    dependence profile cannot — how long each region actually takes — which is
    what turns "how much work is in here" into "how much time would this save".
    """
    def run_cmd(cmd: List[str], cwd: Path, env: Dict[str, str]) -> "tuple[bool, str]":
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env)
        except OSError as e:
            return False, str(e)
        return r.returncode == 0, (r.stderr or r.stdout or "")

    if (dp_dir / "hotspot_detection" / "Hotspots.json").exists():
        return True, "reusing the measurements already in .discopop"
    return impact_mod.run_hotspot_detection(
        args.source_file, dp_dir, args.reprofil_args or None, _venv_env(), run_cmd
    )


def _reprofil_fast(
    source_file: str, discopop_dir: Path, old_text: str, new_text: str,
    output_dir: Path,
) -> "tuple[bool, str]":
    """Refresh the profile WITHOUT running the instrumented program.

    The instrumented run is the step that scales with the workload — 17x native
    on a 104M-operation kernel here, and worse the more memory traffic there is.
    Everything else DiscoPoP needs is static: re-running `discopop_cxx` alone
    regenerates `Data.xml`, `static_dependencies.txt` and the instruction
    mapping for the new code in about a second.

    So the compile runs, and the PREVIOUS run's observed dependences are
    translated onto the new instruction numbering (fast_refresh.py) rather than
    re-measured.  A dependence that cannot be translated with certainty is
    dropped, never guessed: the rewritten region ends up covered by static
    dependences alone, which are over-approximate and can only make the agent
    more cautious.

    Returns (ok, human-readable note).  On any doubt it returns False so the
    caller can fall back to a full re-profile — a wrong dependence is far worse
    than a slow one.
    """
    src = Path(source_file).resolve()
    binary = src.parent / "a.out"
    profiler = (discopop_dir / "profiler").resolve()
    extra = [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"] if Path(_LLVM_LIBCXX).exists() else []
    env = _venv_env()

    lmap = fast_refresh.line_map(old_text, new_text)
    col_shifts = fast_refresh.indent_shifts(old_text, new_text, lmap)
    problems = fast_refresh.verify_translation(old_text, new_text, lmap)
    if problems:
        return False, f"line map failed its own check ({problems[0][:80]})"

    # The compile overwrites the instruction mapping, so the old one — the half
    # of the translation that describes where the dependences came from — has to
    # be taken out of the way first.
    saved: "dict[str, str]" = {}
    for name in _RUN_ARTIFACTS + ("instructionID_to_lineID_mapping.txt",):
        f = profiler / name
        if f.exists():
            saved[name] = f.read_text()
    if "dynamic_dependencies.txt" not in saved or "instructionID_to_lineID_mapping.txt" not in saved:
        return False, "no previous profile to carry forward"

    r = subprocess.run(
        [_cxx_wrapper(), str(src), "-o", str(binary)] + extra,
        capture_output=True, text=True, cwd=src.parent, env=env,
    )
    if r.returncode != 0:
        return False, f"instrumentation failed: {r.stderr[-200:]}"

    old_map = output_dir / ".fast_refresh_old_mapping.txt"
    old_map.write_text(saved["instructionID_to_lineID_mapping.txt"])
    new_map = profiler / "instructionID_to_lineID_mapping.txt"

    dep_text, stats = fast_refresh.remap_dependencies(
        saved["dynamic_dependencies.txt"], old_map, new_map, lmap, col_shifts
    )
    (profiler / "dynamic_dependencies.txt").write_text(dep_text)
    if "loop_counter_output.txt" in saved:
        (profiler / "loop_counter_output.txt").write_text(
            fast_refresh.remap_loop_counters(saved["loop_counter_output.txt"], lmap)
        )
    if "reduction.txt" in saved:
        (profiler / "reduction.txt").write_text(
            fast_refresh.remap_reduction(saved["reduction.txt"], lmap)
        )
    # Memory-region ids are runtime identities the carried dependences still
    # refer to by name, so this file travels unchanged.
    if "memory_regions.txt" in saved:
        (profiler / "memory_regions.txt").write_text(saved["memory_regions.txt"])
    old_map.unlink(missing_ok=True)

    r = subprocess.run(
        [_explorer_cmd()], capture_output=True, text=True,
        cwd=discopop_dir.resolve(), env=env,
    )
    if r.returncode != 0:
        return False, f"explorer failed on the refreshed profile: {r.stderr[-200:]}"

    return True, stats.summary()


def _reprofil(source_file: str, discopop_dir: Path, binary_args: list | None = None) -> bool:
    """Re-instrument, run, and re-explore after a Tier-2 patch is accepted."""
    src = Path(source_file).resolve()   # absolute path avoids CWD confusion
    binary = src.parent / "a.out"
    extra = [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"] if Path(_LLVM_LIBCXX).exists() else []
    env = _venv_env()

    r = subprocess.run(
        [_cxx_wrapper(), str(src), "-o", str(binary)] + extra,
        capture_output=True, text=True, cwd=src.parent, env=env,
    )
    if r.returncode != 0:
        print(f"      [re-profile] instrumentation failed:\n{r.stderr[-500:]}")
        return False

    run_cmd = [str(binary)] + (binary_args or [])
    subprocess.run(run_cmd, capture_output=True, text=True, cwd=src.parent, env=env)

    r = subprocess.run(
        [_explorer_cmd()], capture_output=True, text=True,
        cwd=discopop_dir.resolve(), env=env,
    )
    if r.returncode != 0:
        print(f"      [re-profile] explorer failed:\n{r.stderr[-500:]}")
        return False

    return True
