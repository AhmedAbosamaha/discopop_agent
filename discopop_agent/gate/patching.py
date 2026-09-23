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
import os
import shlex
from pathlib import Path
from typing import Callable, List, Optional, Tuple

from .. import project as project_mod
from .toolchain import (_LIBOMP_DIR, _macos_sysroot_flag, compiler_for, link_flags_for,
                        omp_build_flags, uses_omp_runtime)


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
    out: List[str] = []
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


def run_patch(target: Path, patch_path: Path, exact: bool = False) -> Tuple[bool, str]:
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

    `exact=True` adds -F0.  GNU patch defaults to a fuzz factor of 2, so it will
    apply a hunk whose CONTEXT does not match — verified: a hunk carrying
    `// CTX ONE CHANGED` against a file holding `// CTX ONE` applied cleanly and
    exited 0.  That is tolerable when validating a candidate (the result is
    checked afterwards anyway), but it breaks the invariant the change-log
    REPLAY rests on: `_apply_change_log` treats "this patch no longer applies" as
    the signal that a change depended on one that was dropped.  Fuzz turns that
    signal into a silent apply somewhere near the intended place.
    """
    try:
        r = subprocess.run(
            # --no-backup-if-mismatch: suppress <file>.orig backups on fuzzy apply.
            # --reject-file: a failed hunk otherwise drops <target>.rej beside
            # the target, and one caller's target is the USER'S SOURCE FILE.
            # Send rejects next to the patch instead, which always lives in a
            # temp dir or the agent's own output dir.
            ["patch", "--batch", "--forward", "--quiet",
             "--no-backup-if-mismatch",
             f"--reject-file={patch_path}.rej"]
            + (["-F0"] if exact else [])
            + [str(target), str(patch_path)],
            capture_output=True, text=True,
            stdin=subprocess.DEVNULL, timeout=60,
        )
    except subprocess.TimeoutExpired:
        return False, "patch timed out after 60 s (it should take milliseconds)"
    Path(f"{patch_path}.rej").unlink(missing_ok=True)
    if r.returncode != 0:
        return False, (r.stdout + r.stderr).strip() or f"patch exited {r.returncode}"
    return True, ""


def run_build(
    source: Path, clangpp: str, out: Path, flags: List[str], work_dir: Path,
    transform_all: Optional[Callable[[str], str]] = None,
) -> "subprocess.CompletedProcess[str]":
    """Build the program whose file under test is `source`, into `out`.

    THE build seam: every compile the gate performs goes through here.  For a
    single-file program `source` is the program and this is the one command each
    site used to run itself.  For a project (`project.active()`), `source` holds
    the candidate content of ONE file — the focus — and the program is built for
    real: the tree is staged into a fresh directory under `work_dir`, the candidate
    replaces the focus file there, and every unit is compiled.  The user's tree is
    only ever read.

    `transform_all` rewrites every staged unit before the build (the schedule
    stress build declares `schedule(runtime)` program-wide this way); for a single
    file the caller has already applied it to `source`.
    """
    proj = project_mod.active()
    if proj is None:
        cmd = [compiler_for(source, clangpp), str(source), "-o", str(out)] + flags
        return subprocess.run(cmd, capture_output=True, text=True, cwd=work_dir)

    focus = project_mod.focus()
    staged = work_dir / f"_dp_proj_{out.name}"
    shutil.rmtree(staged, ignore_errors=True)
    proj.stage(staged, {focus: source.read_text()} if focus else None)
    if transform_all is not None:
        for unit in proj.units:
            f = staged / unit
            if f.exists() and unit != focus:
                f.write_text(transform_all(f.read_text()))
    compiler = compiler_for(source, clangpp)
    try:
        if proj.build_cmd:
            # The project's own build.  Flags reach it through the conventional
            # variables AND as placeholders, since Makefiles differ in which they
            # honour; -fopenmp / -fsanitize have to reach compile and link alike.
            joined = " ".join(shlex.quote(f) for f in flags + list(proj.cflags))
            env = dict(os.environ)
            for var in ("CFLAGS", "CXXFLAGS", "LDFLAGS", "DP_FLAGS"):
                env[var] = joined
            env.update({"CC": compiler, "CXX": compiler, "DP_OUT": str(out)})
            cmd_text = (proj.build_cmd.replace("{flags}", joined).replace("{out}", shlex.quote(str(out)))
                        .replace("{cc}", shlex.quote(compiler)).replace("{cxx}", shlex.quote(compiler)))
            r = subprocess.run(["/bin/sh", "-c", cmd_text], capture_output=True, text=True,
                               cwd=staged, env=env)
            built = staged / proj.binary
            if r.returncode == 0 and not out.exists() and built.exists():
                shutil.copy2(built, out)
            if r.returncode == 0 and not out.exists():
                r = subprocess.CompletedProcess(r.args, 1, r.stdout, (r.stderr or "")
                                                + f"\nthe build command produced neither {out} nor {proj.binary}")
            return r
        cmd = ([compiler] + proj.unit_paths(staged) + proj.include_flags(staged)
               + ["-o", str(out)] + flags + list(proj.cflags) + list(proj.ldflags))
        return subprocess.run(cmd, capture_output=True, text=True, cwd=staged)
    finally:
        # The binary has been written to `out`; the staged sources are dead weight,
        # and there is one of these per build.
        shutil.rmtree(staged, ignore_errors=True)


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
    extra = link_flags_for(source) + _macos_sysroot_flag()
    # A program that calls the OpenMP runtime cannot link without it (Fix 92); every
    # other program is still compiled plain, which is what this stage is for.
    omp = omp_build_flags() if uses_omp_runtime(source.read_text()) else []
    result = run_build(source, clangpp, binary, ["-g", "-O1"] + omp + extra, work_dir)
    if result.returncode != 0:
        return False, result.stderr[-2000:]
    return True, ""


def _compile_variant(
    source: Path, clangpp: str, work_dir: Path, name: str, openmp: bool,
    optimize: str = "-O2", extra_flags: Optional[List[str]] = None,
    transform_all: Optional[Callable[[str], str]] = None,
) -> Tuple[bool, str, Optional[Path]]:
    """Compile `source` to a runnable binary, with or without OpenMP.

    Both the correctness and performance stages want the SAME `-O2 -fopenmp`
    binary, and `validate()` builds it once and memoises it.  The speedup
    comparison no longer builds a second, non-OpenMP variant: it varies
    OMP_NUM_THREADS on this one binary instead, so identical machine code sits
    on both sides of the ratio (see `_measure_speedup`).  `openmp=False` is what a
    PRAGMA-FREE rewrite gets (validate() passes `openmp=has_pragma`): nothing in
    such a diff can run in parallel, so -fopenmp could only add codegen noise to
    the comparison.

    `extra_flags` carries the semantically neutral codegen switches the
    numerical calibration varies (contraction, vectorization) — see
    `equivalence.numerical_noise_floor`.
    """
    binary = work_dir / name
    extra = link_flags_for(source) + (
        [f"-I{Path(_LIBOMP_DIR).parent / 'include'}", f"-L{_LIBOMP_DIR}", f"-Wl,-rpath,{_LIBOMP_DIR}"]
        if (openmp and Path(_LIBOMP_DIR).exists()) else []
    ) + _macos_sysroot_flag()
    flags = [optimize] + (["-fopenmp"] if openmp else []) + list(extra_flags or []) + extra
    result = run_build(source, clangpp, binary, flags, work_dir, transform_all)
    if result.returncode != 0:
        return False, result.stderr[-1500:], None
    return True, "", binary
