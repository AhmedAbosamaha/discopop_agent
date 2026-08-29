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

import shutil
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
    "memory_regions.txt",
)

# NOT a run artifact, despite having been treated as one.  `discopop_cxx` alone
# writes reduction.txt, and writes it CORRECTLY for the new source: after the
# array_accumulator rewrite that turns `acc[0] += x` into a local `sum`, a
# compile-only run of the instrumenter produces
#     FileID : 1 Loop Line Number : 18 Reduction Line Number : 22
#     Variable Name : sum Operation Name : +
# — the right loop, the right line, the NEW variable.  Carrying the previous
# run's copy forward overwrote that with a translation of the OLD record, whose
# reduction line no longer maps (it was rewritten), so `remap_reduction` dropped
# it and the loop lost its `reduction` classification entirely.  DiscoPoP then
# reported a plain `do_all` on an accumulation loop, which is a race.
# By contrast loop_counter_output.txt is written by the compile but left EMPTY
# (0 bytes) until the binary runs, so that one really does have to be carried.
# Kept as the anchor for the `reduction carry` regression check, which fails
# if reduction.txt is ever moved back into _RUN_ARTIFACTS.  It drives no
# behaviour of its own any more: the profiler directory is cleared wholesale
# before the compile, so every compile artifact is regenerated regardless.
_COMPILE_ARTIFACTS = ("reduction.txt",)


def _measure_hotspots(args: AgentArguments, dp_dir: Path,
                      force: bool = False) -> "tuple[bool, str]":
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

    existing = dp_dir / "hotspot_detection" / "Hotspots.json"
    if existing.exists():
        if not force:
            return True, "reusing the measurements already in .discopop"
        # A rewrite moved the lines these are keyed on, so they have to be
        # re-measured rather than reused.
        existing.unlink()
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

    # discopop_cxx APPENDS to EVERY artifact it writes; it never truncates.
    # Compiling into a .discopop that still holds the previous source's analysis
    # therefore produces a profile describing TWO programs merged.  Measured on
    # array_accumulator after one rewrite, the fast-refreshed profile against a
    # clean full profile of the SAME source:
    #     Data.xml            935 lines vs 491      instruction mapping 186 vs 96
    #     ast_dump.json     65199 lines vs 32697    static deps          50 vs 27
    # — almost exactly double, across the board.  That is what inflated the
    # pattern count (5 do_all instead of 2 plus a reduction), put two compiles'
    # instruction ids in one mapping, and anchored a blocker to a line that was
    # a loop only in the OLD source.  It also compounds: fast-chain adds another
    # copy per refresh, which is why it diverges roughly twice as much as
    # fast-step.  So the directory is emptied and rebuilt from the compile, with
    # only the genuine RUN artifacts restored on top.
    # Measured: after the array_accumulator rewrite that replaces `acc[0] += x`
    # with a local `sum`, reduction.txt ended up holding BOTH
    #   Loop Line Number : 17 ... Variable Name : _ZZ4mainE3acc   (stale)
    #   Loop Line Number : 18 ... Variable Name : sum             (correct)
    # and line 17 in the new source is `long long sum = 0;` — not a loop at all.
    # A full re-profile does not show this because its run rewrites them.
    if profiler.exists():
        shutil.rmtree(profiler, ignore_errors=True)

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
    # reduction.txt is deliberately NOT restored: see _COMPILE_ARTIFACTS above.
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
    """Re-instrument, run, and re-explore after a Tier-2 patch is accepted.

    The profiler directory is emptied first.  `discopop_cxx` APPENDS to every
    artifact it writes and never truncates, so re-profiling in place merges the
    new analysis into the previous one.  Measured by profiling ONE unchanged
    source three times in the same directory:

        Data.xml   444 -> 888 -> 1332      mapping  90 -> 180 -> 270
        static deps 23 ->  46 ->   69

    — a complete extra copy each time.  The agent re-profiles after every kept
    Tier-2 rewrite and once before Phase B, so without this the profile every
    later decision reads describes N+1 merged programs: inflated pattern counts,
    instruction ids from several compiles colliding in one mapping, and blockers
    anchored to lines that were loops only in an earlier version of the source.
    """
    src = Path(source_file).resolve()   # absolute path avoids CWD confusion
    binary = src.parent / "a.out"
    extra = [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"] if Path(_LLVM_LIBCXX).exists() else []
    env = _venv_env()

    profiler = (discopop_dir / "profiler").resolve()
    if profiler.exists():
        shutil.rmtree(profiler, ignore_errors=True)

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
