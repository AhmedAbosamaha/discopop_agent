"""
Variable scope and use analysis for OpenMP clause checking
----------------------------------------------------------
Four questions about a name, answered by reading the source rather than by
compiling it — because the defects these catch are exactly the ones a compiler
accepts.  `private(ok)` on a variable the loop writes and later code reads
builds cleanly, races nowhere and prints the right answer whenever the data
happens to agree; only a static read of the code can see that the writes are
being discarded.

Deliberately crude, and deliberately conservative in one direction: a false
"yes, it is read" costs one rejected pragma, a false "no" ships a silently wrong
program.
"""
from __future__ import annotations

import re
from typing import List


def _without_comments(lines: List[str]) -> List[str]:
    """The same lines with comment text blanked out, indices and indentation kept.

    Comments are prose and read nothing at runtime, but they mention variables:
    a model's own note, `/* Second phase: copy B to A. Independent (i,j) ... */`,
    made `_read_after` see a read of `j` and refused a correct `private(i, j)`
    (local_obs1, jacobi-2d-imper). String literals are left alone: they cannot
    contain a C identifier that matters here, and blanking them would change
    indentation bookkeeping for no gain.
    """
    out: List[str] = []
    in_block = False
    for ln in lines:
        res = []
        i = 0
        while i < len(ln):
            if in_block:
                end = ln.find("*/", i)
                if end < 0:
                    res.append(" " * (len(ln) - i))
                    i = len(ln)
                else:
                    res.append(" " * (end + 2 - i))
                    i = end + 2
                    in_block = False
            elif ln.startswith("//", i):
                res.append(" " * (len(ln) - i))
                i = len(ln)
            elif ln.startswith("/*", i):
                in_block = True
                res.append("  ")
                i += 2
            else:
                res.append(ln[i])
                i += 1
        out.append("".join(res))
    return out


def _declared_in(lines: List[str], name: str) -> bool:
    """Is `name` DECLARED anywhere in these lines (not merely used)?"""
    decl = re.compile(
        r"(?:^|[;{}(,]|\s)"                       # statement boundary
        r"(?:const\s+|static\s+|volatile\s+|unsigned\s+|signed\s+)*"
        r"(?:auto|bool|char|short|int|long|float|double|size_t|"
        r"[A-Za-z_]\w*(?:::\w+)*)"                # a type name
        r"[\s*&]+"
        r"(?:[\w\s,*&]*?\b)?"                     # other names in the same decl
        + re.escape(name) + r"\b\s*(?=[=;,\[)])"
    )
    return any(decl.search(ln) for ln in lines)


_LOOP_HEAD = re.compile(r"^\s*(?:for|while)\s*\(")


def _body_writes_first(lines: List[str], span: "tuple[int, int]", word: "re.Pattern[str]",
                       assign_only: "re.Pattern[str]") -> bool:
    """Does the loop at `span` write the name before its body reads it, on every iteration?

    Conservative: only when the FIRST line of the body that mentions the name is a
    plain assignment to it (`name = expr;`, the name absent from `expr`) at the body's
    own top level — the indentation of the body's first statement, so the write is
    not under an `if` and runs on every iteration before anything else can see the
    name.  Anything subtler counts as a read, which costs at most a rejected pragma.
    """
    start, end = span
    body = lines[start + 1:end + 1]
    top = next((len(ln) - len(ln.lstrip()) for ln in body
                if ln.strip() and ln.strip() not in ("{", "}")), None)
    if top is None:
        return False                 # a one-line loop: the body sits in the header
    for ln in body:
        if not word.search(ln) or ln.lstrip().startswith("#"):
            continue
        if assign_only.match(ln) and len(ln) - len(ln.lstrip()) == top:
            return not word.search(ln.split("=", 1)[1])
        return False
    return False


def _read_after(lines: List[str], name: str, after_idx: int,
                stop_indent: "int | None" = None) -> bool:
    """Is `name` READ somewhere after line `after_idx`, before it is redeclared?

    Deliberately crude and deliberately conservative in the direction that
    matters: any mention that is not a plain assignment to the name counts as a
    read.  A false "yes" costs one rejected pragma; a false "no" ships a silently
    wrong program.

    This used to stop after a fixed 60 lines, which contradicted that very
    principle: the same `private(ok)` defect was caught with the read 40 lines
    below the loop and MISSED with it 70 lines below, purely on distance.  The
    search now runs to the end of the ENCLOSING BLOCK instead — `stop_indent` is
    the loop header's indentation, and a `}` at or left of it closes the scope
    the variable lives in.  That is bounded by structure rather than by an
    arbitrary count, and it cannot be escaped by padding.
    """
    from .parse import _loop_span

    lines = _without_comments(lines)
    word = re.compile(r"\b" + re.escape(name) + r"\b")
    assign_only = re.compile(r"^\s*" + re.escape(name) + r"\s*=[^=]")
    # A later loop whose header starts by assigning the name: `for (j = 0; ...)`.
    # Every use of `j` inside that loop reads the value the header just wrote,
    # never the one the parallel loop left behind, so the whole loop is skipped.
    # Uses AFTER it are still examined — if the loop ran zero times (it may sit
    # inside another loop), the old value survives and a later read sees it.
    # Without this, every PolyBench kernel was refused `private(j)`: the counters
    # are declared once per function and the next loop nest re-initialises them.
    init_kill = re.compile(r"^\s*for\s*\(\s*" + re.escape(name) + r"\s*=(?!=)([^;]*);")
    i = after_idx + 1
    while i < len(lines):
        ln = lines[i]
        if stop_indent is not None:
            stripped = ln.strip()
            if stripped.startswith("}") and (len(ln) - len(ln.lstrip())) <= stop_indent:
                return False          # left the block the name is declared in
        # A later loop whose body WRITES the name before anything in it reads it
        # (Fix 91).  The same reasoning as `init_kill`, one step further in: every
        # use inside that body sees the value the body itself just wrote, never the
        # one the parallel loop left behind.  `s281` (E1, reps 2-5): the agent split
        # the loop at LEN/2, DiscoPoP's `private(x)` on the first half was refused
        # because the second half mentions `x` — as `x = ...` first, then reads.
        # Uses AFTER the skipped loop are still examined (it may run zero times).
        if not word.search(ln) and _LOOP_HEAD.match(ln):
            span = _loop_span(lines, i)
            if span is not None and span[1] > i and _body_writes_first(lines, span, word, assign_only):
                i = span[1] + 1
                continue
        if not word.search(ln):
            i += 1
            continue
        if ln.lstrip().startswith("#"):
            # A directive is not a runtime read: the name in a later
            # `#pragma omp parallel for private(j, k)` is a clause for the NEXT
            # loop, and counting it as a read refused every correct pragma in a
            # kernel with two loop nests in a row (2mm, jacobi-2d-imper).
            i += 1
            continue
        if _declared_in([ln], name):     # shadowed / redeclared — stop looking
            return False
        kill = init_kill.match(ln)
        if kill and not word.search(kill.group(1)):
            span = _loop_span(lines, i)
            if span is not None and span[1] >= i:
                i = span[1] + 1
                continue
        if assign_only.match(ln):
            i += 1
            continue
        return True
    return False


def _strip_loop_header(line: str) -> str:
    """Whatever follows the `for (...)` / `while (...)` control clause on `line`.

    A one-line loop puts the header and the body on the SAME line, and the
    clause rules used to scan `body[1:]` — dropping that line wholesale and with
    it the only write there is.  `for (...) { ok = 0; }` was therefore accepted
    under `private(ok)` no matter what came after it.  Parens are matched by
    counting, so a header like `for (int i=0; i<f(x); i++)` does not truncate
    early.
    """
    m = re.match(r"\s*(?:for|while)\s*\(", line)
    if not m:
        return line
    depth = 0
    for i in range(m.end() - 1, len(line)):
        if line[i] == "(":
            depth += 1
        elif line[i] == ")":
            depth -= 1
            if depth == 0:
                return line[i + 1:]
    return ""


def _declared_as_array(lines: List[str], name: str) -> bool:
    """Is `name` declared with ARRAY storage, as opposed to a pointer to it?

    The distinction decides whether writing `name[i]` counts as writing `name`
    for the clause rules.  `private` on an array gives each thread its own
    copy, so the element writes are thrown away; `private` on a POINTER copies
    the pointer, and the writes still land in the one shared buffer.  Treating
    the two alike would reject correct pointer pragmas.
    """
    sub = re.compile(r"\b" + re.escape(name) + r"\s*\[")
    return any(_declared_in([ln], name) and sub.search(ln) for ln in lines)


def _written_in(lines: List[str], name: str, subscript: bool = False) -> bool:
    """Is `name` ASSIGNED anywhere in these lines?

    The write-back rule only bites when the loop actually produces a value.  A
    read-only scalar in `firstprivate` — a loop bound, a size, a function
    parameter — is correct and idiomatic OpenMP, and rejecting it was throwing
    away five of six good pragmas.

    `subscript` also counts `name[expr] = ...`, which is what an array-valued
    clause turns into.  Off by default because it is only sound once the name
    is known to BE an array — see _declared_as_array.
    """
    pat = re.compile(
        r"\b" + re.escape(name) + r"\s*(?:"
        r"(?<![=!<>+\-*/%&|^])=(?!=)"      # x = ...   (not ==, !=, <=, +=, ...)
        r"|\+=|-=|\*=|/=|%=|&=|\|=|\^=|<<=|>>="
        r"|\+\+|--"                        # x++ / x--
        r")"
    )
    pre = re.compile(r"(?:\+\+|--)\s*\b" + re.escape(name) + r"\b")   # ++x / --x
    elem = re.compile(
        r"\b" + re.escape(name) + r"\s*\[[^\]]*\]\s*"
        r"(?:(?<![=!<>+\-*/%&|^])=(?!=)|\+=|-=|\*=|/=|%=|&=|\|=|\^=)"
    ) if subscript else None
    return any(pat.search(ln) or pre.search(ln)
               or (elem is not None and elem.search(ln)) for ln in lines)
