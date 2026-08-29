"""
Changing the user's source file, reversibly
--------------------------------------------
Every write to the real file goes through here, and every one of them is
undoable: the original is backed up before the first change, and the whole run
can be rebuilt from the ordered change log by replaying it onto the original.

Rebuilding by REPLAY rather than by un-applying is deliberate.  A patch is never
reversed; a change that stood on one that has been dropped simply fails to
apply, and that failure is the signal that it has to go too.
"""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from ..args import AgentArguments
from ..llm import make_diff, normalize_code
from ..gate.patching import fix_hunk_headers, run_patch


def _function_edit_to_diff(
    source_file: str, start_line: int, end_line: int, new_code: str
) -> str | None:
    """--edit-mode function: splice the LLM's rewritten function into the file
    over [start_line, end_line] and return a unified diff of the change.

    The diff is generated from the actual on-disk content, so it always applies
    cleanly — eliminating the diff-apply failure class.  Returns None if the span
    is invalid or the edit is a no-op (ignoring comments and whitespace)."""
    old_text = Path(source_file).read_text()
    old_lines = old_text.splitlines(keepends=True)
    if start_line < 1 or end_line > len(old_lines) or start_line > end_line:
        return None
    new_block = [ln + "\n" for ln in new_code.splitlines()]
    new_lines = old_lines[: start_line - 1] + new_block + old_lines[end_line:]
    old_span = "".join(old_lines[start_line - 1: end_line])
    if normalize_code(new_code) == normalize_code(old_span):
        return None
    return make_diff(old_text, "".join(new_lines), source_file)


def _apply_to_source(diff: str, source_file: str, output_dir: Path, label: str) -> bool:
    """Write a validated patch into the real source file, backing the original
    up first.  Returns True if the file now carries the change.

    Tier-2 rewrites were always written back, but a validated Tier-1 pragma used
    to be recorded and then left on disk in patch_generator/ — so a run that
    proved a 5x parallelization ended with the user's source untouched and
    nothing to show for it.  The agent's output is a parallelized program, so
    accepted patches of either tier land in the file.
    """
    src = Path(source_file).resolve()
    backup = output_dir / f"{src.name}.original"
    if not backup.exists():
        shutil.copy2(src, backup)
        print(f"│  [{label}] Original backed up → {backup.name}")
    patch_path = output_dir / f".apply_{label.lower()}.patch"
    patch_path.write_text(fix_hunk_headers(diff) + "\n")
    ok, diag = run_patch(src, patch_path)
    patch_path.unlink(missing_ok=True)
    if not ok:
        print(f"│  [{label}] WARNING: could not apply the validated patch to "
              f"{src.name}: {diag[:160]}")
        return False
    print(f"│  [{label}] Applied to {src.name}")
    return True


def _apply_in_memory(diff: str, source_file: str) -> "str | None":
    """What `source_file` would contain with `diff` applied — without touching
    the real file.  Stages a candidate pragma so it can be timed before the
    decision to keep it is made."""
    with tempfile.TemporaryDirectory(prefix="dp_agent_stage_") as tmp:
        work = Path(tmp)
        dst = work / Path(source_file).name
        shutil.copy2(source_file, dst)
        pf = work / "stage.patch"
        pf.write_text(fix_hunk_headers(diff) + "\n")
        ok, _diag = run_patch(dst, pf)
        return dst.read_text() if ok else None


def _apply_change_log(original_text: str, keep: list, args: AgentArguments) -> list:
    """Write `original_text` to the source, then re-apply `keep` in order.

    Returns the subset that actually applied.  Nothing is ever un-applied, so a
    change that stood on one that has been dropped simply fails here — which is
    the signal that it has to go too.
    """
    src = Path(args.source_file)
    src.write_text(original_text)
    landed: list = []
    with tempfile.TemporaryDirectory(prefix="dp_agent_apply_") as tmp:
        work = Path(tmp)
        for ch in keep:
            pf = work / "rb.patch"
            pf.write_text(fix_hunk_headers(ch["diff"]) + "\n")
            # exact=True: this replay's whole logic is that a change whose
            # foundation was dropped must FAIL here.  Fuzzy matching would let
            # it apply anyway, near the right place, and the signal would be
            # lost.
            ok, _diag = run_patch(src, pf, exact=True)
            if ok:
                landed.append(ch)
    return landed
