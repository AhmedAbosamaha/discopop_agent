"""
A program made of several files
--------------------------------
Everything the agent does to "the source" — stage it, patch it, build it, profile
it — used to mean one file.  `Project` is what it means when the program has
more: a root directory, the translation units that are compiled, where their
headers are, and the flags the build needs.

Two decisions here are the result of measurements, not taste (docs/MULTIFILE.md):

  * PROFILING goes through a generated *unity* translation unit — one file that
    `#include`s every unit.  In this DiscoPoP build the call-path state graph, on
    which the loop-carried classification rests, is constructed from the unit
    containing `main` and nothing links it across units.  Profiled unit by unit,
    a two-file program had both of its recurrences reported as applicable Do-All;
    through a unity unit the same program is analysed exactly as its merged
    single-file form is — and `FileMapping.txt` still names the REAL files with
    their REAL line numbers, because `#include` keeps them in the debug info.

  * BUILDING for the gate is the real thing: the project tree is staged into a
    temp directory, the candidate replaces the one file under test, and every unit
    is compiled the way the program is actually built.  What is judged is what
    ships.
"""
from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

UNIT_SUFFIXES = (".c", ".cpp", ".cc", ".cxx", ".C")
HEADER_SUFFIXES = (".h", ".hpp", ".hh", ".hxx", ".inc")
# Never part of the program: profiles, VCS data, build products, the agent's output.
IGNORED_DIRS = {".discopop", ".git", ".svn", "__pycache__", "build", "cmake-build-debug",
                "CMakeFiles", ".profile_snapshots", ".claude", "node_modules"}
IGNORED_SUFFIXES = (".o", ".obj", ".a", ".so", ".dylib", ".out", ".exe", ".ll", ".bc",
                    ".gch", ".pch", ".dSYM", ".original", ".orig", ".rej")
# A staged copy is made for every build; data sets do not belong in it.
MAX_STAGED_FILE_BYTES = 8 * 1024 * 1024
UNITY_NAME = "dp_agent_unity"


@dataclass(frozen=True)
class Project:
    root: Path
    units: Tuple[str, ...]              # translation units, relative to root, in build order
    include_dirs: Tuple[str, ...] = ()  # relative to root (an absolute path is kept as is)
    cflags: Tuple[str, ...] = ()
    ldflags: Tuple[str, ...] = ()
    build_cmd: str = ""                 # optional: the project's own build, run in the root
    binary: str = "a.out"               # what `build_cmd` produces, relative to the root

    # ------------------------------------------------------------------ discovery
    @classmethod
    def discover(cls, root: "str | Path", units: Optional[List[str]] = None,
                 include_dirs: Optional[List[str]] = None, cflags: Optional[List[str]] = None,
                 ldflags: Optional[List[str]] = None, build_cmd: str = "",
                 binary: str = "a.out") -> "Project":
        """Describe the project at `root`.

        Anything not given is found: every C/C++ source under the root is a unit
        (sorted, so the order is reproducible), and every directory holding a
        header is an include directory.  A project whose layout that does not fit
        says so explicitly with `--project-units` / `--project-include`."""
        base = Path(root).resolve()
        found_units: List[str] = []
        header_dirs: List[str] = []
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = sorted(d for d in dirnames if d not in IGNORED_DIRS
                                 and not d.endswith(".dSYM"))
            rel_dir = Path(dirpath).relative_to(base)
            for fn in sorted(filenames):
                if fn.startswith(UNITY_NAME):
                    continue
                if fn.endswith(UNIT_SUFFIXES):
                    found_units.append((rel_dir / fn).as_posix())
                elif fn.endswith(HEADER_SUFFIXES) and rel_dir.as_posix() not in header_dirs:
                    header_dirs.append(rel_dir.as_posix())
        return cls(
            root=base,
            units=tuple(units if units else found_units),
            include_dirs=tuple(include_dirs if include_dirs is not None else header_dirs),
            cflags=tuple(cflags or ()), ldflags=tuple(ldflags or ()),
            build_cmd=build_cmd, binary=binary,
        )

    # ------------------------------------------------------------------ paths
    @property
    def is_cxx(self) -> bool:
        return any(not u.endswith(".c") for u in self.units)

    def rel(self, path: "str | Path") -> Optional[str]:
        """Project-relative spelling of `path`, or None when it lies outside the root."""
        try:
            return Path(path).resolve().relative_to(self.root).as_posix()
        except ValueError:
            return None

    def abs(self, rel: str) -> Path:
        return (self.root / rel).resolve()

    def contains(self, path: "str | Path") -> bool:
        return self.rel(path) is not None

    # ------------------------------------------------------------------ staging
    def stage(self, dest: Path, replace: Optional[Dict[str, str]] = None) -> Path:
        """Copy the program into `dest` and return the staged root.

        `replace` maps project-relative paths to the text they are to hold in the
        copy — the candidate under test.  The real tree is only ever read."""
        dest.mkdir(parents=True, exist_ok=True)
        for dirpath, dirnames, filenames in os.walk(self.root):
            dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS
                           and not d.endswith(".dSYM")]
            rel_dir = Path(dirpath).relative_to(self.root)
            (dest / rel_dir).mkdir(parents=True, exist_ok=True)
            for fn in filenames:
                src = Path(dirpath) / fn
                if fn.endswith(IGNORED_SUFFIXES) or fn.startswith(UNITY_NAME):
                    continue
                try:
                    if src.is_symlink() or src.stat().st_size > MAX_STAGED_FILE_BYTES:
                        continue
                except OSError:
                    continue
                shutil.copy2(src, dest / rel_dir / fn)
        for rel, text in (replace or {}).items():
            target = dest / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        return dest

    # ------------------------------------------------------------------ building
    def include_flags(self, staged_root: Optional[Path] = None) -> List[str]:
        base = staged_root or self.root
        out: List[str] = []
        for d in self.include_dirs:
            p = Path(d)
            out.append(f"-I{p if p.is_absolute() else (base / d)}")
        return out

    def unit_paths(self, staged_root: Optional[Path] = None) -> List[str]:
        base = staged_root or self.root
        return [str(base / u) for u in self.units]

    # ------------------------------------------------------------------ profiling
    def unity_path(self) -> Path:
        return self.root / f"{UNITY_NAME}{'.cpp' if self.is_cxx else '.c'}"

    def unity_text(self) -> str:
        """One translation unit that is the whole program.

        Units are included by their path relative to the root, which is where the
        unity file lives and where the wrapper runs, so the debug information —
        and with it DiscoPoP's FileMapping — names each real file."""
        lines = ["/* Generated by discopop_agent for whole-program profiling. Not part of the",
                 "   program: every unit below is compiled exactly as written. */"]
        lines += [f'#include "{u}"' for u in self.units]
        return "\n".join(lines) + "\n"


def load_file_mapping(discopop_dir: Path) -> Dict[int, Path]:
    """DiscoPoP's file ids: `FileMapping.txt` is `<id>\\t<absolute path>` per line."""
    out: Dict[int, Path] = {}
    f = discopop_dir / "FileMapping.txt"
    if not f.exists():
        return out
    for raw in f.read_text().splitlines():
        parts = raw.split("\t") if "\t" in raw else raw.split(None, 1)
        if len(parts) < 2:
            continue
        try:
            out[int(parts[0])] = Path(parts[1].strip())
        except ValueError:
            continue
    return out


# ---------------------------------------------------------------------------
# The project of the current run, and the file a candidate stands for
# ---------------------------------------------------------------------------
# Every build site in the gate is handed ONE file — a candidate sitting in a temp
# directory — and compiles it.  For a single-file program that file IS the program.
# For a project it is the new content of one file of many, and the build has to be
# told which one: the temp copy's own name says nothing (`before_kern.c`).  That is
# what the focus is.  It is run-level state rather than a parameter because it has
# to reach a dozen call sites unchanged; with no project active every one of them
# behaves exactly as it did before projects existed.
_ACTIVE: Dict[str, object] = {"project": None, "focus": None}


def activate(project: Optional[Project]) -> None:
    _ACTIVE["project"] = project
    _ACTIVE["focus"] = None


def active() -> Optional[Project]:
    p = _ACTIVE["project"]
    return p if isinstance(p, Project) else None


def set_focus(path: "str | Path | None") -> None:
    """Name the project file that candidates handed to the gate stand for."""
    p = active()
    if p is None or path is None:
        _ACTIVE["focus"] = None
        return
    rel = p.rel(path) if Path(str(path)).is_absolute() else Path(str(path)).as_posix()
    _ACTIVE["focus"] = rel


def work_on(args: object, source_file: "str | Path") -> None:
    """Point the run at the file the next region lives in.

    `args.source_file` is "the file under work" everywhere in the phases.  For a
    single-file program that never changes and this does nothing; in a project it
    follows each region to its own file, and the gate's builds follow with it."""
    if active() is None:
        return
    setattr(args, "source_file", str(source_file))
    set_focus(source_file)


def focus() -> Optional[str]:
    f = _ACTIVE["focus"]
    return f if isinstance(f, str) else None
