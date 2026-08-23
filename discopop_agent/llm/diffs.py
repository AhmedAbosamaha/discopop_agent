"""
Getting a usable edit out of a model's reply
----------------------------------------------
Extraction and normalisation only: pull the unified diff or the ```cpp block out
of a response, decide whether it is well-formed, and build a diff from two
versions of a file.  `normalize_code` is what makes "did the model actually
change anything?" ignore comments and whitespace.
"""
from __future__ import annotations

import difflib
import re
from typing import Optional

# The LAST fenced block wins: a reply may open with a short PLAN before the code.
_CODE_FENCE_RE = re.compile(r"```(?:cpp|c\+\+|cxx|c)?\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


# ---------------------------------------------------------------------------
# Diff validation
# ---------------------------------------------------------------------------


def _extract_diff(text: str) -> Optional[str]:
    """Pull the unified diff out of the response.  A short plain-text PLAN is
    allowed before it (see _OUTPUT_DIFF), so scan for the header rather than
    assuming the diff starts at line 0.  A '--- ' line only starts the diff if
    the NEXT line is its '+++ ' partner; that way a stray dash-run or a plan
    line beginning with '---' does not swallow the real header."""
    lines = text.splitlines()
    fallback = None
    for i, line in enumerate(lines):
        if line.startswith("diff --git"):
            return "\n".join(lines[i:])
        if line.startswith("--- "):
            if i + 1 < len(lines) and lines[i + 1].startswith("+++ "):
                return "\n".join(lines[i:])
            if fallback is None:
                fallback = i
    return "\n".join(lines[fallback:]) if fallback is not None else None


def _is_valid_diff(diff: str) -> bool:
    return "---" in diff and "+++" in diff and "@@" in diff


def make_diff(old_text: str, new_text: str, path: str) -> str:
    """Unified diff between two full file contents, safe for `patch`.

    Both edit modes that build their own diff go through here.  The subtlety is
    a file whose last line has no newline: difflib then emits an unterminated
    '-' line that runs straight into the following '+' line, producing a patch
    the apply stage rejects as malformed.  Standard unified-diff form marks that
    case explicitly instead, which GNU and BSD patch both accept."""
    diff = difflib.unified_diff(
        old_text.splitlines(keepends=True),
        new_text.splitlines(keepends=True),
        fromfile=path,
        tofile=path,
    )
    out = []
    for line in diff:
        out.append(line if line.endswith("\n")
                   else line + "\n\\ No newline at end of file\n")
    return "".join(out)


def normalize_code(text: str) -> str:
    """Strip comments and all whitespace so a 'rewrite' that only reformats or
    re-comments the input is recognised as the no-op it is."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", "", text)
    return re.sub(r"\s+", "", text)


def _extract_code(text: str) -> Optional[str]:
    """For --edit-mode function: pull the rewritten function out of the response.
    Prefer the LAST fenced ```cpp block (the response may open with a short PLAN,
    and the final block is the code the model was told to end with); otherwise
    use the raw text.  Returns None if it doesn't look like a function (no
    braces)."""
    matches = list(_CODE_FENCE_RE.finditer(text))
    code = (matches[-1].group(1) if matches else text).strip("\n")
    if "{" in code and "}" in code:
        return code
    return None
