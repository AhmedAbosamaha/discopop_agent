"""
L4 Execution & Validation Layer
---------------------------------
Three-stage quality gate for every LLM-generated patch:

  Stage 1 — Apply   : patch must apply cleanly to an isolated copy
  Stage 2 — Compile : patched file must compile (plain clang++, not instrumented)
  Stage 3 — TSan    : compile with -fsanitize=thread and run; no DATA RACE reports

On any failure the diagnostic text is returned so L3 can include it in
the next retry prompt.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from .types import ValidationResult

# Prefer LLVM 19 clang++ (same toolchain used for the profiler)
_CLANGPP_CANDIDATES = [
    "/usr/local/Cellar/llvm@19/19.1.7/bin/clang++",
    "/usr/local/bin/clang++-19",
    "clang++-19",
    "clang++",
]
_LLVM_LIBCXX = "/usr/local/Cellar/llvm@19/19.1.7/lib/c++"
# macOS: libomp is keg-only (brew install libomp); add its lib dir if present
_LIBOMP_DIR = "/usr/local/opt/libomp/lib"

def _macos_sysroot_flag() -> list:
    """Return -isysroot flag pointing at the available macOS SDK, or []."""
    import subprocess, platform
    if platform.system() != "Darwin":
        return []
    try:
        sdk = subprocess.check_output(["xcrun", "--show-sdk-path"],
                                      text=True, stderr=subprocess.DEVNULL).strip()
        return ["-isysroot", sdk] if sdk else []
    except Exception:
        return []


def _find_clangpp() -> Optional[str]:
    for candidate in _CLANGPP_CANDIDATES:
        p = Path(candidate)
        if p.is_absolute() and p.exists():
            return str(p)
        if shutil.which(candidate):
            return shutil.which(candidate)
    return None


# ---------------------------------------------------------------------------
# Diff normalisation: fix off-by-one line counts in @@ headers
# ---------------------------------------------------------------------------

import re as _re

_HUNK_RE = _re.compile(r"^(@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@)(.*)")


def _fix_hunk_headers(diff: str) -> str:
    """Re-derive old/new line counts from the diff body and rewrite @@ headers.

    LLMs frequently miscalculate the line counts in unified-diff hunk headers
    (e.g. write +21,20 when the body actually provides 18 new lines).  The GNU
    patch utility is strict about these counts and fails with 'malformed patch'
    when they are wrong.  This function fixes the headers so minor counting
    errors don't discard an otherwise correct patch.
    """
    lines = diff.splitlines()
    out: list = []
    i = 0
    while i < len(lines):
        m = _HUNK_RE.match(lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue

        old_start = int(m.group(2))
        new_start = int(m.group(4))
        suffix = m.group(6)  # anything after the closing @@

        # Scan the body of this hunk to recount
        j = i + 1
        old_count = 0
        new_count = 0
        while j < len(lines):
            ln = lines[j]
            if ln.startswith("@@") or ln.startswith("--- ") or ln.startswith("+++ "):
                break
            if ln.startswith("-"):
                old_count += 1
            elif ln.startswith("+"):
                new_count += 1
            else:
                old_count += 1
                new_count += 1
            j += 1

        out.append(f"@@ -{old_start},{old_count} +{new_start},{new_count} @@{suffix}")
        i += 1
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Stage 1: apply patch
# ---------------------------------------------------------------------------

def _apply(diff: str, source_file: str, work_dir: Path) -> Tuple[bool, str, Optional[Path]]:
    src = Path(source_file)
    dst = work_dir / src.name
    shutil.copy2(src, dst)

    diff = _fix_hunk_headers(diff)

    # Rewrite --- / +++ paths to point at our working copy
    fixed_lines = []
    for line in diff.splitlines():
        if line.startswith("--- "):
            fixed_lines.append(f"--- {dst}")
        elif line.startswith("+++ "):
            fixed_lines.append(f"+++ {dst}")
        else:
            fixed_lines.append(line)
    patch_path = work_dir / "llm.patch"
    patch_path.write_text("\n".join(fixed_lines) + "\n")

    result = subprocess.run(
        ["patch", "--quiet", str(dst), str(patch_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        diag = (result.stdout + result.stderr).strip()
        return False, f"patch failed:\n{diag}", None
    return True, "", dst


# ---------------------------------------------------------------------------
# Stage 2: compile
# ---------------------------------------------------------------------------

def _compile(source: Path, clangpp: str, work_dir: Path) -> Tuple[bool, str]:
    binary = work_dir / "validate_binary"
    extra = (
        [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"]
        if Path(_LLVM_LIBCXX).exists() else []
    ) + _macos_sysroot_flag()
    cmd = [clangpp, str(source), "-o", str(binary), "-g", "-O1"] + extra
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
    if result.returncode != 0:
        return False, result.stderr[-2000:]
    return True, ""


# ---------------------------------------------------------------------------
# Stage 3: ThreadSanitizer
# ---------------------------------------------------------------------------

def _tsan(source: Path, clangpp: str, work_dir: Path) -> Tuple[bool, str]:
    binary = work_dir / "tsan_binary"
    extra = (
        [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"]
        if Path(_LLVM_LIBCXX).exists() else []
    ) + (
        [f"-L{_LIBOMP_DIR}", f"-Wl,-rpath,{_LIBOMP_DIR}"]
        if Path(_LIBOMP_DIR).exists() else []
    ) + _macos_sysroot_flag()
    # -fopenmp is required so that #pragma omp parallel for actually runs in
    # parallel; without it TSan never sees cross-thread access on loop vars.
    cmd = [
        clangpp, str(source), "-o", str(binary),
        "-fsanitize=thread", "-fopenmp", "-g", "-O1",
    ] + extra
    compile_result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
    if compile_result.returncode != 0:
        return False, f"TSan compile failed:\n{compile_result.stderr[-1000:]}"

    try:
        run_result = subprocess.run(
            [str(binary)], capture_output=True, text=True, timeout=60, cwd=work_dir
        )
    except subprocess.TimeoutExpired:
        return False, "TSan run timed out (60 s)"

    stderr = run_result.stderr
    if "WARNING: ThreadSanitizer" in stderr or "DATA RACE" in stderr:
        # Extract just the first warning block (up to and including the first SUMMARY line)
        warning_idx = stderr.find("WARNING: ThreadSanitizer")
        if warning_idx >= 0:
            snippet = stderr[warning_idx:]
            summary_idx = snippet.find("SUMMARY: ThreadSanitizer")
            if summary_idx >= 0:
                newline_after = snippet.find("\n", summary_idx)
                snippet = snippet[: newline_after + 1 if newline_after >= 0 else summary_idx + 200]
        else:
            snippet = stderr[-1000:]
        return False, f"Race detected:\n{snippet}"
    return True, ""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate(diff: str, source_file: str) -> ValidationResult:
    """Run all three quality-gate stages. Return the first failure or success."""
    clangpp = _find_clangpp()
    if clangpp is None:
        return ValidationResult(
            passed=False, stage="compile",
            diagnostic="No supported clang++ found (checked 19-based paths)",
        )

    with tempfile.TemporaryDirectory(prefix="dp_agent_val_") as tmp:
        work_dir = Path(tmp)

        # Stage 1
        ok, diag, patched = _apply(diff, source_file, work_dir)
        if not ok:
            return ValidationResult(passed=False, stage="apply", diagnostic=diag)

        # Stage 2
        ok, diag = _compile(patched, clangpp, work_dir)
        if not ok:
            return ValidationResult(passed=False, stage="compile", diagnostic=diag)

        # Stage 3
        ok, diag = _tsan(patched, clangpp, work_dir)
        if not ok:
            return ValidationResult(passed=False, stage="tsan", diagnostic=diag)

    return ValidationResult(passed=True, stage="accepted")
