"""
Turning a pragma into a patch that applies to the file as it stands
-------------------------------------------------------------------
DiscoPoP generates its patches once, against the source as it was profiled.
Phase B then applies them one after another, and every applied pragma shifts
every line below it — so a stored diff stops applying as soon as one lands.
`derive_pragma_patch` rebuilds the patch from (pragma text, loop header) against
the CURRENT file instead, which is what lets more than one pragma survive.

`_repair_pragma_clauses` fixes the one generated defect that is free to fix: a
loop-body local listed in `shared()`, which is either redundant or not in scope.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from ..evidence import _brace_match_end
from ..llm import make_diff
from .parse import (_HUNK_OLD_RE, _PRAGMA_LINE_RE,
                    _PRAGMA_SHARED_RE, _locate_header, _pragma_and_anchor,
                    _touched_span)
from .scope import _declared_in


def _repair_pragma_clauses(diff: "str | None", source_file: str) -> "str | None":
    """Drop names from a generated pragma's `shared()` clause when they are not
    in scope at the pragma.

    DiscoPoP sometimes lists a loop-BODY local in `shared()`.  Observed on
    example4: for a loop whose body opens `int tmp = arr[i];` it emitted
    `shared(tmp,arr)`, and the -fopenmp build then fails outright with
    "use of undeclared identifier 'tmp'".  The gate correctly rejects that
    pattern, but the only recovery was Tier-2 — an LLM call, gated by
    --restructure-depth — for what is a one-token defect in a generated clause.
    Deleting the name is not restructuring, so it happens here instead: at any
    depth, for free, before the gate.

    Only `shared()` is touched, and that makes the repair semantically free:
    a variable from an enclosing scope is shared by DEFAULT in a `parallel for`,
    so removing it from the clause cannot change the meaning — it is either
    redundant or (the bug case) not in scope at all.  `private`, `firstprivate`,
    `lastprivate` and `reduction` are left alone, since removing a name there
    WOULD change semantics.  A pragma carrying `default(none)` is skipped
    entirely, because there the clause is load-bearing.

    Returns the diff unchanged (same object) when there is nothing to fix, so
    the gate cache key is unaffected.
    """
    if not diff or "#pragma omp" not in diff:
        return diff

    try:
        src_lines = Path(source_file).read_text().splitlines()
    except OSError:
        return diff

    out: List[str] = []
    old_line = 0           # 1-based line in the ORIGINAL file
    changed = False

    for line in diff.splitlines():
        m = _HUNK_OLD_RE.match(line)
        if m:
            old_line = int(m.group(1))
            out.append(line)
            continue

        if line.startswith("+") and "#pragma omp" in line and "default(none)" not in line:
            # The pragma is inserted BEFORE original line `old_line`, which is
            # the loop it applies to.  Its body is that loop's brace span.
            body: List[str] = []
            if 0 < old_line <= len(src_lines):
                end = _brace_match_end(source_file, old_line)
                if end >= old_line:
                    body = src_lines[old_line - 1:end]
            if body:
                def _strip(mm: "re.Match") -> str:
                    names = [n.strip() for n in mm.group(1).split(",") if n.strip()]
                    kept = [n for n in names if not _declared_in(body, n)]
                    if len(kept) == len(names):
                        return str(mm.group(0))
                    dropped = [n for n in names if n not in kept]
                    print(f"│  [Tier-1] Repairing the generated pragma: "
                          f"{', '.join(dropped)} "
                          f"{'is' if len(dropped) == 1 else 'are'} declared inside "
                          f"the loop body, so cannot appear in shared()")
                    return f"shared({','.join(kept)})" if kept else ""

                fixed = str(_PRAGMA_SHARED_RE.sub(_strip, line))
                if fixed != line:
                    changed = True
                    line = fixed.rstrip() + " "
            out.append(line)
            continue

        if not line.startswith("+"):
            # context and removed lines both advance the original-file position
            if not line.startswith("---") and not line.startswith("\\"):
                old_line += 1
        out.append(line)

    return "\n".join(out) + ("\n" if diff.endswith("\n") else "") if changed else diff


def derive_pragma_patch(stored_diff: "str | None", source_file: str) -> "str | None":
    """Rebuild a generated pragma's patch against the CURRENT file.

    DiscoPoP's patches are produced once, against the source as it was profiled.
    Phase B then applies them one after another, and every applied pragma shifts
    every line below it — so the second stored patch already describes a file
    that no longer exists, and `patch` refuses it.  Before `--forward` that hung
    the run; after it, the pragma is silently skipped, which works directly
    against the goal of ending up with MORE pragmas.

    Replaying the stored diff is the mistake.  A pragma is really just two
    facts: the text to insert, and the loop it belongs to.  Locate that loop in
    the file as it stands now and emit a fresh diff, and it applies by
    construction no matter how much has moved above it.
    """
    if not stored_diff:
        return None
    pa = _pragma_and_anchor(stored_diff)
    if pa is None:
        return stored_diff              # not a shape we understand — leave it alone
    pragma, header = pa
    try:
        old_text = Path(source_file).read_text()
    except OSError:
        return stored_diff
    src = old_text.splitlines()
    span = _touched_span(stored_diff)
    head = _locate_header(src, header, (span[0] - 1) if span else 0)
    if head is None:
        return None                     # the loop is gone; the pragma is meaningless
    if head > 0 and src[head - 1].strip() == pragma.strip():
        return None                     # already carries exactly this pragma
    new = src[:head] + [pragma] + src[head:]
    return make_diff(old_text, "\n".join(new) + "\n", source_file)


def _read_tier1_patch(patch_dir: Path) -> str | None:
    """Return the content of the first .patch file DiscoPoP generated for a
    pattern, or None if the patch_generator directory is missing / empty."""
    if not patch_dir.exists():
        return None
    for f in sorted(patch_dir.glob("*.patch")):
        return f.read_text()
    return None


def _already_annotated(diff: str, source_file: str) -> bool:
    """Does the loop this generated patch targets already carry a pragma?

    Under --llm-pragmas this really happens: the LLM annotates a loop, the
    re-profile runs on the annotated source — the instrumented build has no
    -fopenmp, so the pragmas are ignored and the dependences come out
    sequential, exactly as they should — and DiscoPoP then proposes a pattern
    for a loop that is already parallel.  Applying its pragma on top would put
    one worksharing construct directly inside another.
    """
    pa = _pragma_and_anchor(diff)
    if pa is None:
        return False
    _pragma, header = pa
    try:
        src = Path(source_file).read_text().splitlines()
    except OSError:
        return False
    span = _touched_span(diff)
    head = _locate_header(src, header, (span[0] - 1) if span else 0)
    if head is None:
        return False
    for j in range(head - 1, max(head - 4, -1), -1):
        st = src[j].strip()
        if not st or st.startswith("//"):
            continue
        return bool(_PRAGMA_LINE_RE.match(src[j]))
    return False
