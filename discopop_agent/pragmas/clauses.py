"""
Static checks on a pragma's data-sharing clauses
------------------------------------------------
Two rules, applied to every `private` / `firstprivate` name:

  * a name DECLARED inside the loop body is already per-iteration and cannot
    appear in a clause at all — the -fopenmp build fails with "use of undeclared
    identifier";
  * a name the loop WRITES (or, for an array, fills) and code after the loop
    READS must never be private — those clauses discard the writes, so the later
    read sees a stale value and the program keeps running with a wrong answer.

The second rule is the reason this module exists.  On example4 DiscoPoP emitted
`private(ok)` for a sortedness check; the result compiles, races nowhere, and
prints "sorted: YES" even with the sort deleted.  Compile, ThreadSanitizer and
output comparison all pass it.  Nothing but a static read catches it.

The same rules apply whoever wrote the pragma: `check_pragma_clauses` reads
DiscoPoP's generated patch, `check_llm_pragmas` reads an LLM's edit against the
PATCHED text, since the loops it annotates do not exist in the file yet.
"""
from __future__ import annotations

from pathlib import Path
from typing import List

from .parse import (_PRAGMA_LINE_RE, _PRIVATE_CLAUSE_RE,
                    _loop_span, _locate_header, _next_loop_header,
                    _pragma_and_anchor, _touched_span)
from ..sources.edits import _apply_in_memory
from .scope import _declared_as_array, _declared_in, _read_after, _written_in


def check_pragma_clauses(diff: "str | None", source_file: str) -> "str | None":
    """Reject a generated pragma whose data-sharing clauses cannot be right.

    Returns None when the pragma is acceptable, or a one-line reason when it is
    not.  Static: nothing is compiled or executed.

    This exists because the runtime gate structurally cannot see the worst case.
    On example4, DiscoPoP emitted `private(ok)` for

        int ok = 1;
        for (...) if (arr[i] > arr[i+1]) ok = 0;
        printf(... ok ? "YES" : "NO");

    `private` gives each thread its own uninitialised copy and discards it at
    the end of the region, so the writes never reach the `ok` that printf reads.
    The program then prints "sorted: YES" even with the sort deleted — verified.
    It compiles, races nowhere (each thread owns its copy), and prints
    byte-identical output whenever the array really is sorted, so compile, TSan
    and correctness all pass it.  Only this check sees it.

    Two rules, both about a name that must not be in the clause at all:
      - read after the loop  -> its value has to survive; `private` severs that
        and `firstprivate` copies in without copying out.
      - declared inside the body -> not in scope at the pragma; the -fopenmp
        build fails with "use of undeclared identifier" (the `private(tmp)`
        case, which at least fails loudly).
    """
    if not diff or "#pragma omp" not in diff:
        return None
    try:
        src = Path(source_file).read_text().splitlines()
    except OSError:
        return None

    # The pragma and the loop it governs, as they will look once applied.
    added = [l[1:] for l in diff.splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    pragma = next((l for l in added if "#pragma omp" in l), None)
    if pragma is None:
        return None
    # The loop this pragma governs is the next loop header AFTER IT IN THE DIFF.
    # Line arithmetic from the hunk start does not work: it picks up whichever
    # loop happens to sit nearby, which on example4 meant checking the array-init
    # loop instead of the one the pragma was attached to.
    pa = _pragma_and_anchor(diff)
    if pa is None:
        return None
    _pragma_text, header = pa
    span = _touched_span(diff)
    head = _locate_header(src, header, (span[0] - 1) if span else 0)
    if head is None:
        return None
    return _clause_problem(src, pragma, head)


def _clause_problem(src: List[str], pragma: str, head: int) -> "str | None":
    """The two rules above, applied to ONE pragma governing the loop at `head`.

    Split out from check_pragma_clauses because the rules do not care who wrote
    the pragma — DiscoPoP's generated clauses and the LLM's own are wrong in
    exactly the same two ways, and `private(ok)` is invisible to compile, TSan
    and output whichever of them produced it.
    """
    names: List[str] = []
    for kind, body in _PRIVATE_CLAUSE_RE.findall(pragma):
        for n in body.split(","):
            n = n.strip()
            if n:
                names.append(n)
    if not names:
        return None

    loop = _loop_span(src, head)
    if loop is None:
        return None
    body = src[loop[0]: loop[1] + 1]

    for n in names:
        if _declared_in(body[1:], n):
            return (f"clause names `{n}`, which is declared inside the loop body — "
                    f"it is already per-iteration and is not in scope at the pragma")
        # The write-back rule needs BOTH halves: the loop has to produce a value
        # AND something after the loop has to read it.  A read-only scalar in
        # firstprivate (a bound, a size, a parameter) is perfectly correct.
        is_array = _declared_as_array(src, n)
        if (_written_in(body[1:], n, subscript=is_array)
                and _read_after(src, n, loop[1])):
            what = "fills and later code reads" if is_array else "writes and later code reads"
            return (f"clause names `{n}`, which the loop {what} — "
                    f"private/firstprivate discard those writes, so that "
                    f"read would see a stale value")
    return None


def check_llm_pragmas(diff: "str | None", source_file: str) -> "str | None":
    """The clause rules, run over every pragma the LLM's OWN edit introduces.

    check_pragma_clauses above reads a generated patch: one pragma, inserted
    before a loop that already exists in the file.  An LLM rewrite is neither —
    it may carry several pragmas, and the loops they govern are new code that
    the current file does not contain yet.  So the check runs against the
    PATCHED text instead, over the lines the diff actually wrote.

    Returns None when every pragma is acceptable, or a one-line reason naming
    the offending pragma.  This is the one gate stage that can see a clause
    which compiles, races nowhere, and still silently drops the loop's results
    — see check_pragma_clauses for the `private(ok)` case that motivated it.
    """
    if not diff or "#pragma omp" not in diff:
        return None
    patched = _apply_in_memory(diff, source_file)
    if patched is None:
        return None            # it does not even apply; that is stage 1's answer
    src = patched.splitlines()
    span = _touched_span(diff)
    lo, hi = ((span[0] - 1, span[1] - 1) if span else (0, len(src) - 1))
    for i in range(max(lo, 0), min(hi, len(src) - 1) + 1):
        if not _PRAGMA_LINE_RE.match(src[i]):
            continue
        head = _next_loop_header(src, i)
        if head is None:
            continue
        problem = _clause_problem(src, src[i], head)
        if problem:
            return f"`{src[i].strip()}` — {problem}"
    return None
