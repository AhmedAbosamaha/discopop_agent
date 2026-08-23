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


def _read_after(lines: List[str], name: str, after_idx: int, limit: int = 60) -> bool:
    """Is `name` READ somewhere after line `after_idx`, before it is redeclared?

    Deliberately crude and deliberately conservative in the direction that
    matters: any mention that is not a plain assignment to the name counts as a
    read.  A false "yes" costs one rejected pragma; a false "no" ships a silently
    wrong program.
    """
    word = re.compile(r"\b" + re.escape(name) + r"\b")
    assign_only = re.compile(r"^\s*" + re.escape(name) + r"\s*=[^=]")
    for ln in lines[after_idx + 1: after_idx + 1 + limit]:
        if not word.search(ln):
            continue
        if _declared_in([ln], name):     # shadowed / redeclared — stop looking
            return False
        if assign_only.match(ln):
            continue
        return True
    return False


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
