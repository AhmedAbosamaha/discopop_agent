"""
Locating pragmas, the loops they govern, and the lines a patch touched
---------------------------------------------------------------------
Text-level structure recovery: given a diff or a file, find the `#pragma omp`
lines, the loop header each one applies to, that loop's extent, and the span a
patch rewrote.  Everything here is line-based on purpose — it has to work on a
patch that has not been applied yet, and on source that may not compile.
"""
from __future__ import annotations

import re
from typing import List


_PRAGMA_SHARED_RE = re.compile(r"\bshared\s*\(([^)]*)\)")
_HUNK_OLD_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")
_PRIVATE_CLAUSE_RE = re.compile(r"\b(private|firstprivate)\s*\(([^)]*)\)")
_LOOP_HEAD_RE = re.compile(r"^\s*(for|while)\s*\(")


def _loop_span(lines: List[str], head_idx: int) -> "tuple[int, int] | None":
    """Line range of the loop whose header is at `head_idx`, by brace balance.

    Returns (first, last) 0-based inclusive.  A brace-less single-statement body
    ends at the first line that closes the header's parentheses and then carries
    a `;`, which covers the common `for (...)\n    stmt;` shape.
    """
    depth = 0
    seen_brace = False
    for i in range(head_idx, min(len(lines), head_idx + 400)):
        ln = lines[i]
        for ch in ln:
            if ch == "{":
                depth += 1
                seen_brace = True
            elif ch == "}":
                depth -= 1
                if seen_brace and depth <= 0:
                    return head_idx, i
        if not seen_brace and i > head_idx and ln.rstrip().endswith(";"):
            return head_idx, i
        if not seen_brace and i == head_idx and ln.rstrip().endswith(";") and ")" in ln:
            return head_idx, i
    return None


def _pragma_and_anchor(diff: str) -> "tuple[str, str] | None":
    """From a generated patch, the pragma line it adds and the loop header that
    follows it.  Together those are everything needed to place the pragma
    against ANY version of the file — which is what makes replaying a stored
    diff unnecessary."""
    dl = diff.splitlines()
    pi = next((i for i, l in enumerate(dl)
               if l.startswith("+") and "#pragma omp" in l), None)
    if pi is None:
        return None
    pragma = dl[pi][1:]
    for l in dl[pi + 1:]:
        if l.startswith("-"):
            continue
        text = l[1:] if l[:1] in ("+", " ") else l
        st = text.strip()
        if not st or st.startswith("//") or st.startswith("/*") or st.startswith("*"):
            continue                      # a comment may sit between the two
        if _LOOP_HEAD_RE.match(text):
            return pragma, text
        break
    return None


def _locate_header(src: List[str], header: str, near: int) -> "int | None":
    """Index of `header` in `src`, nearest to `near`.  Identical sibling loops
    are common, so proximity to the patch's own hunk breaks the tie."""
    cands = [i for i, l in enumerate(src) if l.strip() == header.strip()]
    if not cands:
        return None
    return min(cands, key=lambda i: abs(i - near))
_PRAGMA_LINE_RE = re.compile(r"^\s*#\s*pragma\s+omp\b")


def _next_loop_header(src: List[str], after: int, limit: int = 6) -> "int | None":
    """Index of the loop header a pragma at `after` applies to, or None.

    Only blank lines, comments and continued pragma lines may sit between the
    two; anything else means the pragma is not annotating a loop (a `parallel`
    block, a `task`, a `barrier`) and the clause rules do not apply to it.
    """
    for i in range(after + 1, min(len(src), after + 1 + limit)):
        st = src[i].strip()
        if not st or st.startswith("//") or st.startswith("/*") or st.startswith("*"):
            continue
        if src[i - 1].rstrip().endswith("\\") or _PRAGMA_LINE_RE.match(src[i]):
            continue
        return i if _LOOP_HEAD_RE.match(src[i]) else None
    return None
_HUNK_NEW_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def _touched_span(diff: str) -> "tuple[int, int] | None":
    """Line range the patch rewrote, in NEW-file coordinates, from its @@ headers.

    Used to ask the post-restructuring question precisely: did DiscoPoP find a
    pattern *in the code the model actually changed*?  A pattern somewhere else
    in the file proves nothing about this rewrite.  Returns None when no hunk
    header parses (then the caller falls back to file scope).
    """
    lo = hi = None
    for line in diff.splitlines():
        m = _HUNK_NEW_RE.match(line)
        if not m:
            continue
        start = int(m.group(1))
        count = int(m.group(2)) if m.group(2) is not None else 1
        end = start + max(count, 1) - 1
        lo = start if lo is None else min(lo, start)
        hi = end if hi is None else max(hi, end)
    return (lo, hi) if lo is not None and hi is not None else None


def _added_pragmas(diff: str) -> List[str]:
    """The `#pragma omp` lines a diff introduces, in order.

    Under --llm-pragmas this is what turns a restructuring into a
    parallelization: the gate's TSan, correctness and timing stages all key on
    the diff carrying a pragma, and an empty list here means the LLM produced a
    sequential rewrite that still needs DiscoPoP's verdict.
    """
    return [l[1:].strip() for l in diff.splitlines()
            if l.startswith("+") and not l.startswith("+++") and "#pragma omp" in l]
