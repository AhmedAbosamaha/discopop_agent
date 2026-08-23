"""
Applying a patch and building the result
-----------------------------------------
The mechanical half of the gate: get the diff onto a temp copy, then compile it.
`fix_hunk_headers` exists because models miscount `@@` line ranges routinely and
a patch that is correct in content should not be rejected over arithmetic.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple

from .toolchain import _LIBOMP_DIR, _LLVM_LIBCXX, _macos_sysroot_flag


_HUNK_RE = re.compile(r"^(@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@)(.*)")


def fix_hunk_headers(diff: str) -> str:
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
            if ln.startswith("\\"):
                # "\ No newline at end of file" annotates the preceding line;
                # it is not itself a line of either file, so it must not be
                # counted — doing so would corrupt the header we're fixing.
                j += 1
                continue
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


def run_patch(target: Path, patch_path: Path) -> Tuple[bool, str]:
    """Apply `patch_path` to `target`, without any way to hang.

    GNU patch goes INTERACTIVE whenever it cannot work out what to do — "File
    to patch:", "Reversed (or previously applied) patch detected!  Assume -R?"
    — and reads the answer from stdin.  Under subprocess.run(capture_output=True)
    stdout and stderr are piped but stdin is inherited, so those prompts are
    invisible and the call blocks forever.  That really happened: a run sat on
    an unanswerable prompt for six minutes before it was killed.

    Three guards, each closing a different route to a hang:
      --batch            never ask; take the default for every question
      --forward          skip a patch that looks already applied instead of
                         asking about it (the case that hung: an earlier pragma
                         had already changed the lines this patch expected)
      stdin=DEVNULL      any prompt that still appears reads EOF and gives up
      timeout            a backstop — patch works in milliseconds, so anything
                         approaching a minute is pathological
    """
    try:
        r = subprocess.run(
            # --no-backup-if-mismatch: suppress <file>.orig backups on fuzzy apply.
            ["patch", "--batch", "--forward", "--quiet",
             "--no-backup-if-mismatch", str(target), str(patch_path)],
            capture_output=True, text=True,
            stdin=subprocess.DEVNULL, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False, "patch timed out after 60 s (it should take milliseconds)"
    if r.returncode != 0:
        return False, (r.stdout + r.stderr).strip() or f"patch exited {r.returncode}"
    return True, ""


def _apply(diff: str, source_file: str, work_dir: Path) -> Tuple[bool, str, Optional[Path]]:
    src = Path(source_file)
    dst = work_dir / src.name
    shutil.copy2(src, dst)

    diff = fix_hunk_headers(diff)

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

    ok, diag = run_patch(dst, patch_path)
    if not ok:
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


def _compile_variant(
    source: Path, clangpp: str, work_dir: Path, name: str, openmp: bool, optimize: str = "-O2"
) -> Tuple[bool, str, Optional[Path]]:
    """Compile `source` to a runnable binary, with or without OpenMP.

    Both the correctness and performance stages want the SAME `-O2 -fopenmp`
    binary, and `validate()` builds it once and memoises it.  The speedup
    comparison no longer builds a second, non-OpenMP variant: it varies
    OMP_NUM_THREADS on this one binary instead, so identical machine code sits
    on both sides of the ratio (see `_measure_speedup`).  `openmp=False` is
    therefore unused by the gate today and kept only for callers that want a
    genuinely sequential build.
    """
    binary = work_dir / name
    extra = (
        [f"-L{_LLVM_LIBCXX}", f"-Wl,-rpath,{_LLVM_LIBCXX}"]
        if Path(_LLVM_LIBCXX).exists() else []
    ) + (
        [f"-L{_LIBOMP_DIR}", f"-Wl,-rpath,{_LIBOMP_DIR}"]
        if (openmp and Path(_LIBOMP_DIR).exists()) else []
    ) + _macos_sysroot_flag()
    cmd = [clangpp, str(source), "-o", str(binary), optimize]
    if openmp:
        cmd.append("-fopenmp")
    cmd += extra
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)
    if result.returncode != 0:
        return False, result.stderr[-1500:], None
    return True, "", binary
