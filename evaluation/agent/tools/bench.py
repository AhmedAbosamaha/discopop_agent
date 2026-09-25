"""How a packaged benchmark is built and profiled — one answer for every tool.

A packaged benchmark is either one file (`meta["file"]`) or, since decision D6
(THESIS_EXPERIMENTS.md §5g), a project: `meta["project"]` names its translation units and
include directories, and `meta["file"]` is the unit that holds `main` and the harness's
own code. The runner (`cli.py`), the instrument studies (T0.1 `size_table.py`, T0.2
`profile_stability.py`, T0.5 `share_study.py`, T0.6 `dp_main_study.py`) and the packaging
study (T0.8) all need the same three things:

  stage()        copy the benchmark's sources into a scratch directory
  build_inputs() what to hand a plain compiler: the units and -I flags
  wrapper_cmd()  how DiscoPoP's compiler wrapper is invoked — for a project through ONE
                 generated unity unit, compiled by its ABSOLUTE path (see Fix 78 in the
                 agent's FIXES.md: compiled by a relative name, clang records included
                 units as "./src/x.c" and the explorer's variable classification then
                 finds no declarations, so every Do-All loses its clauses)

Nothing here runs anything; the tools keep their own process handling and timeouts.
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_include  # noqa: E402
harness_include.install()   # every build finds prepared/_harness (D39)

SOURCE_SUFFIXES = (".c", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".hh", ".inc")
UNITY_NAME = "dp_harness_unity"


def load_meta(bench_dir: Path) -> dict:
    return json.loads((bench_dir / "meta.json").read_text())


def is_project(meta: dict) -> bool:
    return bool(meta.get("project"))


def is_c(meta: dict) -> bool:
    return meta.get("language", "c") == "c"


def stage(bench_dir: Path, dest: Path, meta: Optional[dict] = None) -> Path:
    """Copy the benchmark's sources into `dest` (created). Returns `dest`."""
    meta = meta or load_meta(bench_dir)
    dest.mkdir(parents=True, exist_ok=True)
    if not is_project(meta):
        shutil.copy2(bench_dir / meta["file"], dest / Path(meta["file"]).name)
        return dest
    for item in sorted(bench_dir.rglob("*")):
        rel = item.relative_to(bench_dir)
        if item.is_file() and rel.suffix in SOURCE_SUFFIXES and ".discopop" not in rel.parts:
            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, dest / rel)
    return dest


def build_inputs(root: Path, meta: dict) -> Tuple[List[str], List[str]]:
    """(inputs, trailing flags) for a plain compiler build of the staged benchmark in `root`.

    Single file: `[<file>]`. Project: every unit plus its include directories, the
    project's own cflags, and its ldflags as the trailing part."""
    if not is_project(meta):
        return [str(root / Path(meta["file"]).name)], []
    proj = meta["project"]
    inputs = ([str(root / u) for u in proj["units"]]
              + [f"-I{root / d}" for d in proj.get("include_dirs") or []]
              + list(proj.get("cflags") or []))
    return inputs, list(proj.get("ldflags") or [])


def wrapper_cmd(root: Path, meta: dict, hotspot: bool = False,
                extra_flags: Optional[List[str]] = None,
                out: str = "a.out") -> Tuple[List[str], Optional[Path]]:
    """DiscoPoP's compiler wrapper invocation for the staged benchmark in `root`.

    Returns (command, unity file or None). The caller runs the command in `root`, and
    unlinks the unity file afterwards — it is not part of the program. The wrapper name
    is bare (`discopop_cc`), resolved through the caller's PATH like everything else."""
    c = is_c(meta)
    stem = "discopop_hotspot_" if hotspot else "discopop_"
    wrapper = f"{stem}{'cc' if c else 'cxx'}"
    libm = ["-lm"] if c else []
    if not is_project(meta):
        return [wrapper, *(extra_flags or []), Path(meta["file"]).name, "-o", out, *libm], None
    proj = meta["project"]
    unity = root / f"{UNITY_NAME}{'.c' if c else '.cpp'}"
    unity.write_text("".join(f'#include "{u}"\n' for u in proj["units"]))
    cmd = [wrapper, *(extra_flags or []), str(unity.resolve()), f"-I{root.resolve()}",
           *[f"-I{(root / d).resolve()}" for d in proj.get("include_dirs") or []],
           *(proj.get("cflags") or []), "-o", out, *(proj.get("ldflags") or []), *libm]
    return cmd, unity


def project_text(root: Path, meta: dict) -> str:
    """The benchmark's sources as one text in a fixed order (for comparisons and checks)."""
    if not is_project(meta):
        return (root / Path(meta["file"]).name).read_text(errors="replace")
    files = sorted(p for p in root.rglob("*")
                   if p.is_file() and p.suffix in SOURCE_SUFFIXES and ".discopop" not in p.parts)
    return "".join(f"/* ==== {p.relative_to(root)} ==== */\n{p.read_text(errors='replace')}\n"
                   for p in files)
