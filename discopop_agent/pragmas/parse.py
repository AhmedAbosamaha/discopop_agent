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


def _locate_header(src: List[str], header: str, near: int,
                   diff: "str | None" = None) -> "int | None":
    """Index of `header` in `src`: the loop the patch `diff` annotates.

    Identical sibling loops are common (PolyBench atax: two `for (j = 0; j < _PB_NY;
    j++)` two lines apart), so the header text alone does not identify the loop.  With
    `diff`, candidates are ranked by how much of the patch's own CONTEXT they reproduce
    — the lines that follow the header (the loop body) and the lines that precede the
    pragma — and only ties are broken by distance to `near`.  Without it, distance alone
    decides, measured from the pragma's line, not from the hunk's first context line:
    that offset of three lines used to put the second sibling's pragma on the first
    (Fix 84)."""
    cands = [i for i, l in enumerate(src) if l.strip() == header.strip()]
    if not cands:
        return None
    before: List[str] = []
    after: List[str] = []
    if diff:
        anchor = _pragma_anchor_index(diff)
        if anchor is not None:
            near = anchor
        before, after = _pragma_context(diff)

    def _agreement(i: int) -> int:
        n = 0
        j = i + 1
        for want in after:                         # the loop body, downwards
            while j < len(src) and _PRAGMA_LINE_RE.match(src[j]):
                j += 1                             # a pragma applied since is not a mismatch
            if j >= len(src) or src[j].strip() != want:
                break
            n, j = n + 1, j + 1
        j = i - 1
        for want in reversed(before):              # what stands above, upwards
            while j >= 0 and _PRAGMA_LINE_RE.match(src[j]):
                j -= 1
            if j < 0 or src[j].strip() != want:
                break
            n, j = n + 1, j - 1
        return n

    return min(cands, key=lambda i: (-_agreement(i), abs(i - near)))
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
_HUNK_OLD_RE = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")


def _pragma_anchor_index(diff: str) -> "int | None":
    """0-based index, in the file the patch was made against, of the line the added
    pragma stands in front of — the loop header, not the hunk's first context line."""
    old_ln = 0
    for line in diff.splitlines():
        m = _HUNK_OLD_RE.match(line)
        if m:
            old_ln = int(m.group(1))
            continue
        if not old_ln or line.startswith(("---", "+++", "\\")):
            continue
        if line.startswith("+"):
            if "#pragma omp" in line:
                return old_ln - 1
            continue
        old_ln += 1
    return None


def _pragma_context(diff: str) -> "tuple[List[str], List[str]]":
    """The patch's unchanged lines around the pragma it adds: (those before the pragma,
    those after the loop header), stripped, blank lines dropped.  Only the hunk that
    holds the pragma is read."""
    before: List[str] = []
    after: List[str] = []
    seen_pragma = seen_header = False
    for line in diff.splitlines():
        if _HUNK_OLD_RE.match(line):
            if seen_pragma:
                break
            before = []
            continue
        if line.startswith(("---", "+++", "\\")):
            continue
        if line.startswith("+"):
            if not seen_pragma and "#pragma omp" in line:
                seen_pragma = True
            continue
        if line.startswith("-"):
            continue
        text = line[1:].strip()
        if not text:
            continue
        if not seen_pragma:
            before.append(text)
        elif not seen_header:
            seen_header = True                     # the loop header itself
        else:
            after.append(text)
    return (before, after) if seen_pragma else ([], [])


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


def changed_span(diff: str) -> "tuple[int, int] | None":
    """Line range a patch really CHANGED, in new-file coordinates — context excluded.

    `_touched_span` reads the hunk headers, which include three lines of context on
    each side; that is right for "did a pattern appear near the change" and too wide
    for "which lines are now spoken for".  Added lines count as themselves; a pure
    deletion counts as the line it was removed after."""
    marks: List[int] = []
    new_ln = 0
    pending_delete = False
    for line in diff.splitlines():
        m = _HUNK_NEW_RE.match(line)
        if m:
            if pending_delete:
                marks.append(max(new_ln - 1, 1))
            new_ln, pending_delete = int(m.group(1)), False
            continue
        if not new_ln or line.startswith(("---", "+++", "\\")):
            continue
        if line.startswith("-"):
            pending_delete = True
            continue
        if line.startswith("+"):
            marks.append(new_ln)
            pending_delete = False      # a replacement: the added lines stand for it
        elif pending_delete:
            marks.append(max(new_ln - 1, 1))
            pending_delete = False
        new_ln += 1
    if pending_delete:
        marks.append(max(new_ln - 1, 1))
    return (min(marks), max(marks)) if marks else None


def _added_pragmas(diff: str) -> List[str]:
    """The `#pragma omp` lines a diff introduces, in order.

    Under --llm-pragmas this is what turns a restructuring into a
    parallelization: the gate's TSan, correctness and timing stages all key on
    the diff carrying a pragma, and an empty list here means the LLM produced a
    sequential rewrite that still needs DiscoPoP's verdict.
    """
    return [l[1:].strip() for l in diff.splitlines()
            if l.startswith("+") and not l.startswith("+++") and "#pragma omp" in l]


def net_new_pragmas(diff: str) -> int:
    """How many `#pragma omp` lines the file GAINS from this diff.

    A diff that re-spells an existing pragma removes one line and adds one: it
    introduces a pragma line (so `_added_pragmas` is non-empty and the gate judges
    it as parallel code, rightly) but adds no parallel loop.  Counting added lines
    alone reported 4 pragmas for a file that held 3."""
    removed = sum(1 for l in diff.splitlines()
                  if l.startswith("-") and not l.startswith("---") and "#pragma omp" in l)
    return max(len(_added_pragmas(diff)) - removed, 0)


_PARALLEL_PRAGMA_RE = re.compile(r"^\s*#\s*pragma\s+omp\s+(?:[a-z ]*\s)?parallel\b")


def existing_parallel_spans(text: str) -> List["tuple[int, int]"]:
    """1-based line spans of the constructs that already run in parallel in `text`.

    A `parallel for` spans its loop; a bare `parallel` spans the block after it.
    Phase B reads this on entry so it never puts DiscoPoP's pragma INSIDE a loop the
    model annotated in Phase A."""
    lines = text.splitlines()
    spans: List["tuple[int, int]"] = []
    for i, ln in enumerate(lines):
        if not _PARALLEL_PRAGMA_RE.match(ln):
            continue
        head = _next_loop_header(lines, i)
        if head is None:
            head = next((j for j in range(i + 1, min(len(lines), i + 8))
                         if lines[j].strip() and not _PRAGMA_LINE_RE.match(lines[j])
                         and not lines[j - 1].rstrip().endswith("\\")), None)
        span = _loop_span(lines, head) if head is not None else None
        if span is not None:
            spans.append((span[0] + 1, span[1] + 1))
    return spans
