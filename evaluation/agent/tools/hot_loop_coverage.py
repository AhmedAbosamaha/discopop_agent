#!/usr/bin/env python3
"""E2-B1's hot-loop coverage check: does the final program's parallel construct cover the hot loop?

Why (record §6, 27 Sep 2026, the author's decision 3 on E2-B1's design). "Parallel" in the verdict
means any `#pragma omp` in the final program (`cli.classify`, `pragmas_in_final`). On a unit whose
hot loop carries a hidden dependence a program can pass the verification with a pragma on a copy
into a temporary, or on an initialisation, while the hot loop stays serial — a verified parallel
program that parallelized nothing that matters. E2-B1's primary outcome therefore counts a program
only when its parallel construct covers the hot loop, checked mechanically: by this module.

THE HOT LOOP is declared by the packager in the package's meta.json (`hot_loop`; E2-B1's suites
only — every other package declares none and its trials record `hot_loop_covered: null`):
  entry     the function the harness times (`kernel_<name>`); the search starts there
  function  the function that holds the hot loop in the package source
  line      the hot loop's first line (its `for`) in the package source
  writes    what the hot loop WRITES, named as the entry function sees it: the base names of the
            left-hand sides of its assignments (`=`, `op=`, `++`, `--`; `memcpy`/`memmove`/`memset`'s
            destination) that write MEMORY — an array element, through a pointer — or UPDATE a scalar
            from itself (`s += ...`, `s = s + ...`, `n++`: the scalar a loop reduces into). Not counted:
            the loop counters (every `for` header), the temporaries the loop declares itself, and a
            scalar merely SET (a scratch value, `s = b[i] * c[i]`; a value carried to the next
            iteration, `t = s`; a pointer re-pointed) — a parallel loop that reuses the hot loop's
            scratch variable must not pass for the hot loop. A callee's pointer parameter is named by
            the caller's argument (s151's `s151s(a, b, 1)`: the callee's `a` is the caller's `a`,
            whatever the callee calls it)
The packager computes `line` and `writes` with `describe` below and refuses a package whose result
differs from the writes it declares by hand (prepare_tsvc.py): the declaration and the verdict read
the C the same way, and a hand-read stands behind both.

THE CRITERION (v1). The final program COVERS the hot loop when code that writes at least one of the
hot loop's `writes` — an array, or the scalar the hot loop reduces into — runs under a thread-parallel
work-sharing construct in the entry function or in a function it calls (transitively):
  counted      any combined construct of `parallel` with a loop directive (`parallel for`,
               `parallel for simd`, `parallel loop`, `target teams distribute parallel for`, ...,
               `parallel master taskloop`); a `for` / `for simd` / `loop` / `taskloop` / `sections`
               bound to a parallel region — lexically inside a `parallel` construct, or in a function
               called from inside one (an orphaned construct).
  NOT counted — each case found is recorded in `uncounted` with its reason, for a hand-read:
    `simd` alone         the vector lanes of ONE thread. The question is whether the hot loop runs on
                         several threads; a `simd` loop does not (the decision this check was asked
                         to take and document, 27 Sep). `parallel for simd` counts, by its `parallel for`.
    a `parallel` region's own code, outside any work-sharing construct: every thread runs all of it.
                         A loop partitioned by hand with omp_get_thread_num() cannot be told from a
                         replicated one by the text, so it is recorded, not counted.
    an explicit `task`   not a work-sharing construct.
    no parallel region   a `for` / `taskloop` / `sections` that no parallel region encloses runs on one
                         thread.
    a serial clause      a literal `num_threads(1)` or `if(0)` / `if(false)`.
    `distribute` alone   teams without `parallel for`; nothing on this host runs it.
The code under a construct is its associated statement and — through every call in it — the callee's
body, with the callee's pointer parameters bound to the call's arguments. Every write is resolved to
the entry function's names the same way: parameters through the call sites, pointer aliases
(`T *p = a;`, `= a + k`, `= &a[k]`, `p = a;`) to what they point into; a value copy (`real_t s = a[i]`)
is not an alias. So:
  * a pragma on the hot loop — covered;
  * a parallel copy loop into a temporary (`pb_tmp[i] = a[i]`), the hot loop serial — NOT covered:
    that loop writes only the temporary;
  * the hot loop split into two parallel loops that write the same array — covered;
  * the pragma inside the callee (s151's `s151s`) — covered, whatever its parameter is called;
  * a `parallel for` on the repetition loop (`nl`) — covered: it contains the hot loop's writes. That
    program is wrong (the repetitions depend on each other through pb_mix): the verification calls it
    BROKEN. This check says only WHERE the parallel construct is; whether the program is correct is
    the verification's verdict, and the primary outcome needs both;
  * the hot loop's values computed into a temporary in parallel and copied back serially — NOT
    covered: the parallel loop writes only the temporary, the hot variables are written serially.
    The text cannot tell that parallel work from the trivial parallel copy above; such a construct
    is listed in `elsewhere` with what it writes, for a hand-read. The mirror case — computed
    serially into a temporary, copied INTO the hot array by a parallel loop — is covered, for the
    same reason: the criterion reads what a construct writes, not how much work it does.
Checked against every archived TSVC trial of E1-E2 (1582 final programs, 27 Sep; the hot loop taken
from each trial's original): no program failed to parse, and every not-covered program with a
pragma was one of the cases above (a parallel copy or precompute into a temporary, a hand-split
`parallel` region, or pragmas only outside the kernel's call graph). s331's trials were left out:
its search loop's only output is a last-value scalar (`j = i`), which is SET, not updated, so under
the rule above that loop has no writes — no verdict (null, with the problem named). An E2-B1 unit
of that shape cannot be packaged until the author rules on it (prepare_tsvc.hot_loop refuses it).

How the C is read: comments and `#if 0` blocks are removed first (a pragma in either does not count),
`\\`-continued pragma lines are joined, `_Pragma("omp ...")` is read as a pragma; a tokenizer and
bracket matching then give the functions, the statements and every construct's associated statement.
Macros are not expanded: a pragma inside a macro body is not seen (the harness's PB_MAIN holds none).
The agent's own helpers (`discopop_agent/pragmas/parse.py`) are line-based by design — they place a
pragma of a patch not yet applied, on a file that may not compile — and know nothing of calls, aliases
or writes, so they are not reused here.

    venv/bin/python evaluation/agent/tools/hot_loop_coverage.py FINAL.c --meta prepared/tsvc_b1/s151/meta.json
    venv/bin/python evaluation/agent/tools/hot_loop_coverage.py --trial runs/<run>/benchmarks/<bench>/<arm>/<model>/rep1
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

CRITERION = "v1 (27 Sep 2026)"

# ---------------------------------------------------------------------------
# Tokens
# ---------------------------------------------------------------------------


@dataclass
class Tok:
    kind: str   # "id", "num", "str", "chr", "op", "pragma"
    text: str   # for a pragma: its text from `omp` on, whitespace collapsed
    line: int


_COMMENT_RE = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'', re.S)
_TOK_RE = re.compile(r"""
    (?P<ws>\s+)
  | (?P<str>"(?:\\.|[^"\\\n])*")
  | (?P<chr>'(?:\\.|[^'\\\n])*')
  | (?P<id>[A-Za-z_]\w*)
  | (?P<num>\.?\d(?:[eEpP][+-]|[\w.])*)
  | (?P<op>\.\.\.|<<=|>>=|->|\+\+|--|<<|>>|<=|>=|==|!=|&&|\|\||[-+*/%&|^]=|::|\S)
""", re.X)
_IF0_RE = re.compile(r"if\s*\(?\s*(?:0|false)\s*\)?\s*$")


def _strip_comments(src: str) -> str:
    """Comments replaced by a blank (their newlines kept, so line numbers hold); strings kept."""
    def repl(m: "re.Match[str]") -> str:
        s = m.group(0)
        return " " + "\n" * s.count("\n") if s.startswith("/") else s
    return _COMMENT_RE.sub(repl, src)


def _preprocess(text: str) -> Tuple[str, List[Tok]]:
    """Blank every preprocessor line (continuations included) and every line of an `#if 0` block;
    return the rest and the `#pragma omp` lines found outside those blocks, as tokens."""
    lines = text.split("\n")
    pragmas: List[Tok] = []
    skipping, depth = False, 0
    i = 0
    while i < len(lines):
        if lines[i].lstrip().startswith("#"):
            j, body = i, lines[i]
            while body.rstrip().endswith("\\") and j + 1 < len(lines):
                body = body.rstrip()[:-1] + " " + lines[j + 1]
                j += 1
            d = body.strip()[1:].strip()
            word = re.match(r"\w*", d).group(0)  # type: ignore[union-attr]
            if skipping:
                if word in ("if", "ifdef", "ifndef"):
                    depth += 1
                elif word == "endif":
                    skipping, depth = (depth > 0), max(depth - 1, 0)
                elif word in ("else", "elif") and depth == 0:
                    skipping = False
            elif word == "if" and _IF0_RE.match(d):
                skipping, depth = True, 0
            elif word == "pragma":
                m = re.match(r"pragma\s+omp\b(.*)$", d, re.S)
                if m:
                    pragmas.append(Tok("pragma", "omp " + " ".join(m.group(1).split()), i + 1))
            for k in range(i, j + 1):
                lines[k] = ""
            i = j + 1
            continue
        if skipping:
            lines[i] = ""
        i += 1
    return "\n".join(lines), pragmas


def tokenize(src: str) -> List[Tok]:
    """The tokens of a C/C++ source, `#pragma omp` lines and `_Pragma("omp ...")` as `pragma` tokens."""
    text, pragmas = _preprocess(_strip_comments(src))
    toks: List[Tok] = []
    line = 1
    for m in _TOK_RE.finditer(text):
        kind = m.lastgroup or "op"
        if kind == "ws":
            line += m.group(0).count("\n")
            continue
        toks.append(Tok(kind, m.group(0), line))
    # A pragma occupies its own (blanked) lines, so it goes before the first token after it.
    out: List[Tok] = []
    pi = 0
    for t in toks:
        while pi < len(pragmas) and pragmas[pi].line < t.line:
            out.append(pragmas[pi])
            pi += 1
        out.append(t)
    out.extend(pragmas[pi:])
    # _Pragma ( "omp ..." ) — the C99 operator form
    res: List[Tok] = []
    k = 0
    while k < len(out):
        t = out[k]
        if (t.kind == "id" and t.text == "_Pragma" and k + 3 < len(out) and out[k + 1].text == "("
                and out[k + 2].kind == "str" and out[k + 3].text == ")"):
            body = out[k + 2].text[1:-1].replace('\\"', '"').replace("\\\\", "\\")
            if re.match(r"\s*omp\b", body):
                res.append(Tok("pragma", "omp " + " ".join(body.strip()[3:].split()), t.line))
            k += 4
            continue
        res.append(t)
        k += 1
    return res


def _match_brackets(toks: Sequence[Tok]) -> List[int]:
    """For every bracket its partner's index (-1 when unmatched; mismatches are tolerated)."""
    match = [-1] * len(toks)
    stack: List[int] = []
    opener = {")": "(", "]": "[", "}": "{"}
    for i, t in enumerate(toks):
        if t.kind != "op":
            continue
        if t.text in ("(", "[", "{"):
            stack.append(i)
        elif t.text in opener:
            k = len(stack) - 1
            while k >= 0 and toks[stack[k]].text != opener[t.text]:
                k -= 1
            if k >= 0:
                j = stack[k]
                del stack[k:]
                match[i], match[j] = j, i
    return match


# ---------------------------------------------------------------------------
# OpenMP directives
# ---------------------------------------------------------------------------

_DIRECTIVE_WORDS = {
    "parallel", "for", "do", "simd", "sections", "section", "single", "master", "masked", "critical",
    "task", "taskloop", "taskgroup", "taskwait", "taskyield", "barrier", "flush", "atomic", "ordered",
    "target", "teams", "distribute", "loop", "declare", "threadprivate", "cancel", "cancellation",
    "point", "data", "enter", "exit", "update", "requires", "scan", "depobj", "workshare", "scope",
    "tile", "unroll", "error", "nothing", "metadirective", "interop", "allocate", "assume", "assumes",
    "dispatch", "begin", "end",
}
_STANDALONE_FIRST = {
    "barrier", "flush", "taskwait", "taskyield", "threadprivate", "declare", "cancel", "cancellation",
    "requires", "scan", "depobj", "error", "nothing", "allocate", "interop", "assumes", "begin", "end",
}
_LOOP_WORDS = {"for", "do", "loop", "taskloop"}
_SERIAL_RE = re.compile(r"\bnum_threads\s*\(\s*1\s*\)|\bif\s*\(\s*(?:parallel\s*:\s*)?(?:0|false)\s*\)")


def directive_words(text: str) -> List[str]:
    """The directive name of a pragma's text (`omp parallel for private(x)` -> parallel, for)."""
    parts = re.findall(r"\w+|\S", text)
    words: List[str] = []
    for k in range(1, len(parts)):
        w, nxt = parts[k], (parts[k + 1] if k + 1 < len(parts) else "")
        if w not in _DIRECTIVE_WORDS or (nxt == "(" and w != "critical"):
            break
        words.append(w)
        if nxt == "(":
            break
    return words


def _standalone(text: str, words: List[str]) -> bool:
    """A directive with no associated statement (or one this check does not model)."""
    if not words or words[0] in _STANDALONE_FIRST:
        return True
    if words[0] == "ordered" and re.search(r"\b(depend|doacross)\s*\(", text):
        return True
    return words[0] == "target" and len(words) > 1 and words[1] in ("update", "enter", "exit")


# ---------------------------------------------------------------------------
# The program: functions, declarations, calls, writes
# ---------------------------------------------------------------------------

_TYPE_KEYWORDS = {
    "void", "char", "short", "int", "long", "float", "double", "signed", "unsigned", "_Bool", "bool",
    "_Complex", "auto", "wchar_t", "size_t", "ssize_t", "ptrdiff_t", "intptr_t", "uintptr_t",
    "int8_t", "int16_t", "int32_t", "int64_t", "uint8_t", "uint16_t", "uint32_t", "uint64_t", "FILE",
    # the harnesses' own element types, defined in headers this check does not read
    "real_t", "DATA_TYPE",
}
_QUALIFIERS = {"const", "volatile", "restrict", "__restrict", "__restrict__", "static", "extern",
               "register", "inline", "__inline", "__inline__", "typename", "constexpr", "mutable"}
_KEYWORDS = {
    "if", "else", "for", "while", "do", "switch", "case", "default", "break", "continue", "return",
    "goto", "sizeof", "typedef", "struct", "union", "enum", "_Pragma", "__attribute__", "defined",
    "new", "delete", "throw", "try", "catch", "namespace", "using", "template", "class", "operator",
    "alignof", "_Alignof", "static_assert", "_Static_assert", "decltype", "this",
} | _TYPE_KEYWORDS | _QUALIFIERS
_ASSIGN_OPS = {"=", "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=", "<<=", ">>="}
# library calls that write through their first argument
_MEM_WRITERS = {"memcpy", "memmove", "memset", "strcpy", "strncpy", "bzero"}
_MAX_CALL_DEPTH = 8


@dataclass
class Param:
    name: str
    pointer: bool   # a pointer, array or reference: writes through it reach the caller's argument


@dataclass
class Func:
    name: str
    params: List[Param]
    lo: int         # the body's `{`
    hi: int         # the body's `}`
    line: int


@dataclass
class Decl:
    name: str
    pointer: bool = False                                  # declared with `*` / `&`
    inits: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class Call:
    name: str
    idx: int
    args: List[Tuple[int, int]]   # inclusive token ranges; (s, s - 1) for an empty argument


@dataclass
class Construct:
    idx: int                 # the pragma token
    text: str
    words: List[str]
    lo: int                  # its associated statement, inclusive token range
    hi: int

    @property
    def serial(self) -> bool:
        return bool(_SERIAL_RE.search(self.text))


class Program:
    """One C/C++ source read as tokens, with the entry function's call graph."""

    def __init__(self, source: str, entry: Optional[str] = None) -> None:
        self.toks = tokenize(source)
        self.n = len(self.toks)
        self.match = _match_brackets(self.toks)
        self.types = set(_TYPE_KEYWORDS) | self._typedef_names()
        self.funcs = self._functions()
        self._calls: Dict[Tuple[int, int], List[Call]] = {}
        self._aliases: Dict[str, Dict[str, Set[str]]] = {}
        self._fdecls: Dict[str, Dict[str, Decl]] = {}
        self._fresh: Dict[str, Set[str]] = {}
        self._constructs: Dict[str, List[Construct]] = {}
        self.reach: List[str] = self._reachable(entry) if entry in self.funcs else list(self.funcs)
        self._sites: Dict[str, List[Tuple[Func, Call]]] = {}
        self._par_funcs: Optional[Set[str]] = None

    # ---- structure -------------------------------------------------------------------

    def _t(self, i: int) -> str:
        return self.toks[i].text if 0 <= i < self.n else ""

    def _typedef_names(self) -> Set[str]:
        names: Set[str] = set()
        for i, t in enumerate(self.toks):
            if t.kind != "id" or t.text != "typedef":
                continue
            j, last = i + 1, None
            while j < self.n and self.toks[j].text != ";":
                tj = self.toks[j]
                if tj.text == "(" and self._t(j + 1) == "*" and j + 2 < self.n and self.toks[j + 2].kind == "id":
                    last = self.toks[j + 2].text
                    break
                if tj.text in ("{", "(", "[") and self.match[j] > j:
                    j = self.match[j] + 1
                    continue
                if tj.kind == "id":
                    last = tj.text
                j += 1
            if last:
                names.add(last)
        return names

    def _functions(self) -> Dict[str, Func]:
        funcs: Dict[str, Func] = {}
        i = 0
        while i < self.n:
            t = self.toks[i]
            if t.kind == "op" and t.text == "{":
                # `namespace X {` and `extern "C" {` are transparent: their functions are file-scope
                if self._t(i - 1) == "namespace" or self._t(i - 2) == "namespace" or (
                        i > 0 and self.toks[i - 1].kind == "str" and self._t(i - 2) == "extern"):
                    i += 1
                    continue
                k = i - 1
                while k >= 0 and self.toks[k].text in ("const", "noexcept", "override", "final"):
                    k -= 1
                if k >= 0 and self.toks[k].text == ")" and self.match[k] > 0:
                    j = self.match[k]
                    name = self.toks[j - 1] if j > 0 else None
                    if name is not None and name.kind == "id" and name.text not in _KEYWORDS:
                        hi = self.match[i] if self.match[i] > i else self.n - 1
                        funcs[name.text] = Func(name.text, self._params(j + 1, k - 1), i, hi, name.line)
                i = self.match[i] + 1 if self.match[i] > i else i + 1
                continue
            i += 1
        return funcs

    def _split_commas(self, lo: int, hi: int) -> List[Tuple[int, int]]:
        parts: List[Tuple[int, int]] = []
        s, j = lo, lo
        while j <= hi:
            tx = self.toks[j].text
            if tx in ("(", "[", "{") and self.match[j] > j:
                j = self.match[j] + 1
                continue
            if tx == ",":
                parts.append((s, j - 1))
                s = j + 1
            j += 1
        if s <= hi or parts:
            parts.append((s, hi))
        return parts

    def _params(self, lo: int, hi: int) -> List[Param]:
        out: List[Param] = []
        for s, e in self._split_commas(lo, hi):
            toks = self.toks[s:e + 1]
            eq = next((k for k, t in enumerate(toks) if t.text == "="), None)   # a C++ default value
            if eq is not None:
                toks = toks[:eq]
            texts = [t.text for t in toks]
            if not toks or texts == ["void"] or texts == ["..."]:
                continue
            name: Optional[str] = None
            pointer = any(x in ("*", "&", "[") for x in texts)
            for k in range(len(toks) - 2):
                if texts[k] == "(" and texts[k + 1] == "*" and toks[k + 2].kind == "id":
                    name = texts[k + 2]      # `real_t (*A)[N]`, a function pointer
                    break
            if name is None:
                depth = 0
                for t in toks:
                    if t.text in ("[", "("):
                        depth += 1
                    elif t.text in ("]", ")"):
                        depth -= 1
                    elif depth == 0 and t.kind == "id" and t.text not in self.types and t.text not in _KEYWORDS:
                        name = t.text
            if name:
                out.append(Param(name, pointer))
        return out

    def _reachable(self, entry: Optional[str]) -> List[str]:
        """The entry function and every function defined here that it calls, transitively."""
        order: List[str] = []
        todo = [entry] if entry else []
        while todo:
            f = todo.pop(0)
            if f in order or f not in self.funcs:
                continue
            order.append(f)
            fn = self.funcs[f]
            todo += [c.name for c in self.calls_in(fn.lo + 1, fn.hi - 1) if c.name in self.funcs]
        return order

    # ---- statements --------------------------------------------------------------------

    def stmt_end(self, i: int, limit: int) -> int:
        """Index of the last token of the statement that starts at `i` (never beyond `limit`)."""
        if i > limit:
            return limit
        t = self.toks[i]
        if t.kind == "pragma":
            if _standalone(t.text, directive_words(t.text)):
                return i
            return self.stmt_end(i + 1, limit) if i + 1 <= limit else i
        if t.text == "{":
            return min(self.match[i], limit) if self.match[i] > i else limit
        if t.kind == "id":
            nxt = self._t(i + 1)
            if t.text in ("for", "while", "switch") and nxt == "(" and self.match[i + 1] > i:
                return self.stmt_end(self.match[i + 1] + 1, limit)
            if t.text == "if" and nxt == "(" and self.match[i + 1] > i:
                e = self.stmt_end(self.match[i + 1] + 1, limit)
                if e + 1 <= limit and self._t(e + 1) == "else":
                    return self.stmt_end(e + 2, limit)
                return e
            if t.text == "else":
                return self.stmt_end(i + 1, limit)
            if t.text == "do":
                e = self.stmt_end(i + 1, limit)
                k = e + 1
                if self._t(k) == "while" and self._t(k + 1) == "(" and self.match[k + 1] > k:
                    k = self.match[k + 1]
                    return min(k + 1 if self._t(k + 1) == ";" else k, limit)
                return e
            if t.text == "case":
                j = i + 1
                while j <= limit and self.toks[j].text != ":":
                    j += 1
                return self.stmt_end(j + 1, limit)
            if (t.text == "default" or t.text not in _KEYWORDS) and nxt == ":" and self._t(i + 2) != ":":
                return self.stmt_end(i + 2, limit)          # a label
        j = i
        while j <= limit:
            tx = self.toks[j].text
            if tx in ("(", "[", "{") and self.match[j] > j:
                j = self.match[j] + 1
                continue
            if tx == ";":
                return j
            if tx == "}":
                return max(j - 1, i)
            j += 1
        return limit

    def constructs(self, f: Func) -> List[Construct]:
        if f.name not in self._constructs:
            out: List[Construct] = []
            for p in range(f.lo + 1, f.hi):
                t = self.toks[p]
                if t.kind != "pragma":
                    continue
                words = directive_words(t.text)
                if _standalone(t.text, words) or p + 1 >= f.hi:
                    continue
                out.append(Construct(p, t.text, words, p + 1, self.stmt_end(p + 1, f.hi - 1)))
            self._constructs[f.name] = out
        return self._constructs[f.name]

    def for_loops(self, lo: int, hi: int) -> List[Tuple[int, int, int]]:
        """(the `for`, its header's `)`, its last token) of every `for` loop in the range."""
        out: List[Tuple[int, int, int]] = []
        for j in range(lo, hi + 1):
            if self.toks[j].kind == "id" and self.toks[j].text == "for" and self._t(j + 1) == "(" \
                    and self.match[j + 1] > j:
                close = self.match[j + 1]
                out.append((j, close, self.stmt_end(close + 1, hi)))
        return out

    # ---- declarations ------------------------------------------------------------------

    def _decl_at(self, j: int, hi: int) -> List[Decl]:
        """The declarators of a declaration starting at `j` (empty when it is not one)."""
        k, saw_type = j, False
        while k <= hi:
            t = self.toks[k]
            if t.kind != "id":
                break
            if t.text in ("struct", "union", "enum"):
                saw_type = True
                k += 1
                if k <= hi and self.toks[k].kind == "id":
                    k += 1
                if k <= hi and self.toks[k].text == "{" and self.match[k] > k:
                    k = self.match[k] + 1
                continue
            if t.text in _QUALIFIERS:
                k += 1
                continue
            if t.text in self.types:
                saw_type = True
                k += 1
                continue
            if t.text in _KEYWORDS:
                return []
            nxt = self.toks[k + 1] if k + 1 < self.n else None
            if not saw_type and nxt is not None and (
                    (nxt.kind == "id" and nxt.text not in _KEYWORDS)
                    or (nxt.text in ("*", "&") and k + 2 < self.n and self.toks[k + 2].kind == "id"
                        and self._t(k + 3) in ("=", ";", ",", "[", ")"))):
                saw_type = True          # an unknown type name: `mytype x`, `mytype *p = ...`
                k += 1
                continue
            break
        if not saw_type:
            return []
        out: List[Decl] = []
        while k <= hi:
            pointer = False
            while k <= hi and (self.toks[k].text in ("*", "&", "&&") or self.toks[k].text in _QUALIFIERS):
                pointer = pointer or self.toks[k].text in ("*", "&", "&&")
                k += 1
            if k > hi:
                break
            name: Optional[str] = None
            if self.toks[k].text == "(" and self.match[k] > k:
                inner = [t for t in self.toks[k + 1:self.match[k]]]
                pointer = pointer or any(t.text == "*" for t in inner)
                ids = [t.text for t in inner if t.kind == "id" and t.text not in _KEYWORDS]
                name = ids[0] if ids else None
                k = self.match[k] + 1
            elif self.toks[k].kind == "id" and self.toks[k].text not in _KEYWORDS:
                name = self.toks[k].text
                k += 1
            if name is None:
                break
            while k <= hi and self.toks[k].text in ("[", "(") and self.match[k] > k:
                k = self.match[k] + 1        # array dimensions; a function declarator's parameters
            d = Decl(name, pointer)
            if k <= hi and self.toks[k].text == "=":
                s = k + 1
                e = s
                while e <= hi and self.toks[e].text not in (",", ";"):
                    if self.toks[e].text in ("(", "[", "{") and self.match[e] > e:
                        e = self.match[e] + 1
                        continue
                    if self.toks[e].text in (")", "]", "}"):
                        break
                    e += 1
                d.inits.append((s, e - 1))
                k = e
            out.append(d)
            if k <= hi and self.toks[k].text == ",":
                k += 1
                continue
            break
        return out

    def decls_in(self, lo: int, hi: int) -> Dict[str, Decl]:
        """Every variable declared in the range (a for-init included), by name."""
        out: Dict[str, Decl] = {}
        for j in range(lo, hi + 1):
            prev = self.toks[j - 1] if j > 0 else None
            start = j == lo or prev is None or prev.text in (";", "{", "}") or prev.kind == "pragma" or (
                prev.text == "(" and self._t(j - 2) == "for")
            if not start or self.toks[j].kind != "id":
                continue
            for d in self._decl_at(j, hi):
                old = out.get(d.name)
                if old is None:
                    out[d.name] = d
                else:
                    old.pointer = old.pointer or d.pointer
                    old.inits += d.inits
        return out

    def expr_base(self, s: int, e: int) -> Optional[str]:
        """The variable a pointer-valued expression points into: `a`, `a + k`, `&a[k]`, `(T *)a`;
        None for a call (`malloc(...)`), a constant, or nothing."""
        k = s
        while k <= e:
            t = self.toks[k]
            if t.text == "(" and self.match[k] > k:
                inner = self.toks[k + 1:self.match[k]]
                if inner and all(x.text in self.types or x.text in _QUALIFIERS or x.text in ("*", "struct")
                                 for x in inner) and self.match[k] < e:
                    k = self.match[k] + 1     # a cast
                    continue
                k += 1                        # a grouping parenthesis
                continue
            if t.text in ("&", "*", "+", "-"):
                k += 1
                continue
            if t.kind == "id" and t.text not in _KEYWORDS and t.text not in self.types:
                if self._t(k + 1) == "(" or t.text in ("NULL", "nullptr"):
                    return None               # a call's result; no memory at all
                return t.text
            return None
        return None

    # ---- calls -------------------------------------------------------------------------

    def calls_in(self, lo: int, hi: int, skip: Sequence[Tuple[int, int]] = ()) -> List[Call]:
        key = (lo, hi)
        if not skip and key in self._calls:
            return self._calls[key]
        out: List[Call] = []
        for j in range(lo, hi + 1):
            t = self.toks[j]
            if t.kind != "id" or t.text in _KEYWORDS or self._t(j + 1) != "(" or self.match[j + 1] <= j:
                continue
            if any(a <= j <= b for a, b in skip):
                continue
            prev = self.toks[j - 1] if j > 0 else None
            if prev is not None and prev.kind == "id" and (prev.text in self.types or prev.text in _QUALIFIERS):
                continue                      # a declaration, not a call
            close = self.match[j + 1]
            args = self._split_commas(j + 2, close - 1) if close > j + 2 else []
            out.append(Call(t.text, j, args))
        if not skip:
            self._calls[key] = out
        return out

    def _call_sites(self, name: str) -> List[Tuple[Func, Call]]:
        if name not in self._sites:
            self._sites[name] = [(self.funcs[g], c) for g in self.reach
                                 for c in self.calls_in(self.funcs[g].lo + 1, self.funcs[g].hi - 1) if c.name == name]
        return self._sites[name]

    # ---- writes ------------------------------------------------------------------------

    def _lvalue(self, k: int, lo: int) -> Tuple[Optional[str], bool]:
        """The base variable of the lvalue that ENDS at token `k` — `a[i]` -> a, `(*A)[i][j]` -> A,
        `p->x[i]` -> p, `s.f` -> s, `*p` -> p — and whether it writes MEMORY (through a subscript,
        `->` or `*`) rather than the variable itself."""
        if k < lo:
            return None, False
        j, start = k, k
        while j >= lo:
            t = self.toks[j]
            if t.kind == "op" and t.text in (")", "]") and self.match[j] >= lo and self.match[j] < j:
                start = self.match[j]
                j = self.match[j] - 1
                continue
            if t.kind == "id":
                start = j
                if j - 1 >= lo and self.toks[j - 1].text in (".", "->"):
                    j -= 2
                    continue
            break
        mem = any(self.toks[x].text in ("[", "->", "*") for x in range(start, k + 1))
        if not mem and start - 1 >= lo and self.toks[start - 1].text == "*":
            before = self.toks[start - 2] if start - 2 >= 0 else None
            mem = before is None or not (before.kind in ("id", "num") and before.text not in _KEYWORDS
                                         or before.text in (")", "]"))
        return self._first_name(start, k), mem

    def _first_name(self, s: int, e: int) -> Optional[str]:
        for j in range(s, e + 1):
            t = self.toks[j]
            if t.kind == "id" and t.text not in _KEYWORDS and t.text not in self.types and self._t(j + 1) != "(":
                return t.text
        return None

    def _rhs_end(self, j: int, hi: int) -> int:
        e = j + 1
        while e <= hi and self.toks[e].text not in (",", ";"):
            if self.toks[e].text in ("(", "[", "{") and self.match[e] > e:
                e = self.match[e] + 1
                continue
            if self.toks[e].text in (")", "]", "}"):
                break
            e += 1
        return e - 1

    def direct_writes(self, lo: int, hi: int, skip: Sequence[Tuple[int, int]] = ()) -> List[Tuple[str, int, str]]:
        """(base name, operator index, kind) of every assignment, `++` and `--` in the range, outside
        the `skip` ranges and outside every `for` header (the loop counters). Kind:
          mem     a write to memory: `a[i] = ...`, `*p = ...`, `p->f = ...`
          update  a variable updated from itself — the scalar a loop REDUCES into: `s += ...`, `n++`,
                  `s = s + ...`, `j = (c) ? i : j`
          set     a variable given a new value: a loop's scratch (`s = b[i] * c[i]`), a value carried to
                  the next iteration (`t = s`), a pointer made to point elsewhere (`p = a`)."""
        masked = list(skip) + [(j + 1, close) for j, close, _ in self.for_loops(lo, hi)]
        out: List[Tuple[str, int, str]] = []
        for j in range(lo, hi + 1):
            if any(a <= j <= b for a, b in masked):
                continue
            t = self.toks[j]
            if t.kind != "op":
                continue
            base: Optional[str] = None
            mem = False
            if t.text in _ASSIGN_OPS:
                base, mem = self._lvalue(j - 1, lo)
            elif t.text in ("++", "--"):
                prev = self.toks[j - 1] if j - 1 >= lo else None
                if prev is not None and ((prev.kind == "id" and prev.text not in _KEYWORDS)
                                         or prev.text in (")", "]")):
                    base, mem = self._lvalue(j - 1, lo)     # postfix
                else:
                    e = j + 1
                    while e <= hi and self.toks[e].text not in (";", ",", ")"):
                        e += 1
                    base = self._first_name(j + 1, e - 1)   # prefix
                    mem = any(self.toks[x].text in ("[", "->", "*") for x in range(j + 1, e))
            if not base:
                continue
            if mem:
                kind = "mem"
            elif t.text != "=":
                kind = "update"
            else:
                e = self._rhs_end(j, hi)
                reads_itself = any(self.toks[x].kind == "id" and self.toks[x].text == base
                                   and self._t(x - 1) not in (".", "->") for x in range(j + 1, e + 1))
                kind = "update" if reads_itself else "set"
            out.append((base, j, kind))
        return out

    def fdecls(self, f: Func) -> Dict[str, Decl]:
        """Every variable declared in `f`'s body."""
        if f.name not in self._fdecls:
            self._fdecls[f.name] = self.decls_in(f.lo + 1, f.hi - 1)
        return self._fdecls[f.name]

    def is_pointer(self, f: Func, name: str) -> bool:
        """`name` is a pointer (or array) parameter or a pointer local of `f`: updating it moves a
        pointer, it writes no memory."""
        d = self.fdecls(f).get(name)
        return (d is not None and d.pointer) or any(p.name == name and p.pointer for p in f.params)

    def aliases(self, f: Func) -> Dict[str, Set[str]]:
        """Pointer locals of `f` -> the variables they are made to point into (flow-insensitive).
        A pointer also given memory of its own (`malloc`, NULL, a call's result) is recorded in
        `_fresh`: it then stands for itself as well (a double buffer swapped with `tmp`)."""
        if f.name not in self._aliases:
            decls = self.fdecls(f)
            amap: Dict[str, Set[str]] = {}
            fresh: Set[str] = set()

            def points(name: str, s: int, e: int) -> None:
                b = self.expr_base(s, e)
                if b and b != name:
                    amap.setdefault(name, set()).add(b)
                elif not b:
                    fresh.add(name)

            for d in decls.values():
                if d.pointer:
                    for s, e in d.inits:
                        points(d.name, s, e)
            for name, j, _ in self.direct_writes(f.lo + 1, f.hi - 1):
                d0 = decls.get(name)
                if (self.toks[j].text == "=" and d0 is not None and d0.pointer
                        and self.toks[j - 1].text == name and self._t(j - 2) not in (".", "->", "*")):
                    points(name, j + 1, self._rhs_end(j, f.hi - 1))
            self._aliases[f.name] = amap
            self._fresh[f.name] = fresh
        return self._aliases[f.name]

    def resolve(self, f: Func, name: str, bindings: Optional[Dict[str, Set[str]]],
                seen: Optional[Set[Tuple[str, str]]] = None) -> Set[str]:
        """The entry-level names `name` in `f` stands for: a pointer alias's target, a pointer
        parameter's arguments (from `bindings` for one call, else from every call site reachable
        from the entry), or itself. A scalar parameter is the callee's own copy: nothing."""
        seen = set() if seen is None else seen
        if (f.name, name) in seen:
            return set()
        seen = seen | {(f.name, name)}
        targets = self.aliases(f).get(name)
        if targets:
            out: Set[str] = {name} if name in self._fresh[f.name] else set()
            for b in targets:
                out |= self.resolve(f, b, bindings, seen)
            return out
        idx = next((k for k, p in enumerate(f.params) if p.name == name), None)
        if idx is None:
            return {name}
        if not f.params[idx].pointer:
            return set()
        if bindings is not None:
            return set(bindings.get(name, set()))
        sites = self._call_sites(f.name)
        if not sites:
            return {name}
        res: Set[str] = set()
        for g, call in sites:
            if idx < len(call.args):
                s, e = call.args[idx]
                arg = self.expr_base(s, e)
                if arg:
                    res |= self.resolve(g, arg, None, seen)
        return res

    def region_writes(self, f: Func, lo: int, hi: int, skip: Sequence[Tuple[int, int]] = (),
                      bindings: Optional[Dict[str, Set[str]]] = None, depth: int = 0) -> Set[str]:
        """What the code in [lo, hi] of `f` writes, as entry-level names, callees included: memory
        (an array element, through a pointer), and the scalars it updates from themselves (the ones a
        loop reduces into). A scalar merely SET — a scratch value, a value carried to the next
        iteration, a pointer re-pointed — is not counted: a parallel loop that reuses the hot loop's
        scratch variable must not pass for the hot loop."""
        local = self.decls_in(lo, hi)
        amap = self.aliases(f)
        out: Set[str] = set()

        def named(name: str) -> Set[str]:
            if name in local and name not in amap:
                return set()                  # a temporary the region declares itself
            return self.resolve(f, name, bindings)

        for name, _, kind in self.direct_writes(lo, hi, skip):
            if kind == "set" or (kind == "update" and self.is_pointer(f, name)):
                continue
            out |= named(name)
        for call in self.calls_in(lo, hi, skip):
            if call.name in _MEM_WRITERS and call.args:
                b = self.expr_base(*call.args[0])
                if b:
                    out |= named(b)
            g = self.funcs.get(call.name)
            if g is None or depth >= _MAX_CALL_DEPTH:
                continue
            bind: Dict[str, Set[str]] = {}
            for p, (s, e) in zip(g.params, call.args):
                b = self.expr_base(s, e) if p.pointer else None
                if b:
                    bind[p.name] = named(b)
            out |= self.region_writes(g, g.lo + 1, g.hi - 1, (), bind, depth + 1)
        return out

    # ---- parallel context --------------------------------------------------------------

    def par_funcs(self) -> Set[str]:
        """Functions called — directly or through other calls — from inside a parallel region."""
        if self._par_funcs is None:
            par: Set[str] = set()
            for g in self.reach:
                for c in self.constructs(self.funcs[g]):
                    if "parallel" in c.words and not c.serial:
                        par |= {x.name for x in self.calls_in(c.lo, c.hi) if x.name in self.funcs}
            todo = list(par)
            while todo:
                fn = self.funcs[todo.pop()]
                for x in self.calls_in(fn.lo + 1, fn.hi - 1):
                    if x.name in self.funcs and x.name not in par:
                        par.add(x.name)
                        todo.append(x.name)
            self._par_funcs = par
        return self._par_funcs

    def in_parallel(self, f: Func, c: Construct) -> bool:
        return f.name in self.par_funcs() or any(
            "parallel" in p.words and not p.serial and p.lo <= c.idx <= p.hi
            for p in self.constructs(f) if p is not c)


# ---------------------------------------------------------------------------
# The hot loop (the packager) and the verdict (the harness)
# ---------------------------------------------------------------------------


def describe(source: str, entry: str, function: str, line: Optional[int] = None,
             repetition_counter: str = "nl") -> Dict[str, Any]:
    """The hot loop's identity for meta.json: the first `for` loop of `function` that is not the
    repetition loop (its header does not set `repetition_counter`) — or the one at `line` — with
    what it writes, named as `entry` sees it."""
    prog = Program(source, entry)
    if function not in prog.funcs:
        raise ValueError(f"{function}: no such function")
    f = prog.funcs[function]
    chosen: Optional[Tuple[int, int, int]] = None
    for kw, close, end in prog.for_loops(f.lo + 1, f.hi - 1):
        init_end = next((j for j in range(kw + 2, close) if prog.toks[j].text == ";"), close)
        counters = {t.text for t in prog.toks[kw + 2:init_end] if t.kind == "id"}
        if (line is not None and prog.toks[kw].line == line) or (line is None and repetition_counter not in counters):
            chosen = (kw, close, end)
            break
    if chosen is None:
        raise ValueError(f"{function}: no hot loop found")
    kw, _, end = chosen
    writes = prog.region_writes(f, kw, end)
    return {"entry": entry, "function": function, "line": prog.toks[kw].line, "writes": sorted(writes)}


def _where(prog: Program, f: Func, c: Construct, hits: Set[str], reason: Optional[str] = None) -> Dict[str, Any]:
    rec: Dict[str, Any] = {"function": f.name, "line": prog.toks[c.idx].line, "directive": "#pragma " + c.text,
                           "writes": sorted(hits)}
    if reason:
        rec["reason"] = reason
    return rec


def coverage(source: str, hot: Dict[str, Any]) -> Dict[str, Any]:
    """The verdict on one final program:
      covered     true when at least one construct covers the hot loop
      covering    those constructs: function, the pragma's line, the directive, the hot variables it writes
      uncounted   parallel-looking constructs that write the hot variables but do not count, with the reason
      elsewhere   the thread-parallel constructs that write none of them, with what they do write — for a
                  hand-read (a rewrite that computes into a temporary in parallel and copies it back
                  serially is NOT covered by the criterion; it shows here)"""
    entry = str(hot["entry"])
    want = set(hot.get("writes") or [])
    res: Dict[str, Any] = {"criterion": CRITERION, "covered": False, "covering": [], "uncounted": [],
                           "elsewhere": []}
    prog = Program(source, entry)
    if entry not in prog.funcs:
        res["problem"] = f"the entry function {entry} is not defined in the final source"
        return res
    if not want:
        res["problem"] = "the hot loop declares no writes"
        return res
    for name in prog.reach:
        f = prog.funcs[name]
        cons = prog.constructs(f)
        for c in cons:
            w = set(c.words)
            if "parallel" in w and not (w & _LOOP_WORDS) and "sections" not in w:
                # a parallel region's OWN code: everything outside the constructs nested in it that
                # distribute the work or run it once (those are judged on their own)
                nested = [(x.idx, x.hi) for x in cons if x is not c and c.lo <= x.idx <= c.hi
                          and set(x.words) & (_LOOP_WORDS | {"sections", "single", "master", "masked", "task"})]
                hits = prog.region_writes(f, c.lo, c.hi, nested) & want
                if hits:
                    why = ("a `parallel master`/`masked` region's own code runs on one thread"
                           if w & {"master", "masked"} else
                           "a `parallel` region's own code outside any work-sharing construct: every thread "
                           "runs all of it (a loop split by hand over omp_get_thread_num() is not recognised)")
                    if c.serial:
                        why = "a literal num_threads(1) / if(0) makes the region run on one thread"
                    res["uncounted"].append(_where(prog, f, c, hits, why))
                continue
            reason: Optional[str]
            if w & _LOOP_WORDS or "sections" in w:
                if c.serial:
                    reason = "a literal num_threads(1) / if(0) makes it run on one thread"
                elif "parallel" in w or prog.in_parallel(f, c):
                    reason = None
                else:
                    reason = "no parallel region encloses it: it runs on one thread"
            elif "simd" in w:
                reason = "`simd` alone: the vector lanes of one thread, not a thread-parallel construct"
            elif "distribute" in w:
                reason = "`distribute` without `parallel for`"
            elif "task" in w:
                reason = "an explicit `task`: not a work-sharing construct"
            else:
                continue                      # single, master, critical, atomic, ordered, ...: not parallel
            writes = prog.region_writes(f, c.lo, c.hi)
            hits = writes & want
            if not hits:
                if reason is None:
                    res["elsewhere"].append(_where(prog, f, c, writes))
                continue
            if reason is None:
                res["covering"].append(_where(prog, f, c, hits))
            else:
                res["uncounted"].append(_where(prog, f, c, hits, reason))
    res["covered"] = bool(res["covering"])
    return res


def trial_fields(hot: Optional[Dict[str, Any]], final_text: str) -> Dict[str, Any]:
    """The fields a trial record carries (cli.py). `hot_loop_covered` is null for a package that
    declares no hot loop — every package before E2-B1 — so no analysis can read "not covered" into
    a record the criterion was never meant for; a check that could not decide is null too, with the
    reason in `hot_loop_coverage.problem`."""
    if not hot:
        return {"hot_loop_covered": None}
    try:
        cov = coverage(final_text, hot)
    except Exception as e:  # noqa: BLE001 — the check must never cost a trial its record
        cov = {"criterion": CRITERION, "covered": None, "problem": f"{type(e).__name__}: {e}"}
    if cov.get("problem"):
        cov["covered"] = None
    return {"hot_loop": hot, "hot_loop_covered": cov["covered"], "hot_loop_coverage": cov}


def main(argv: Optional[Iterable[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", nargs="?", type=Path, help="the final program (with --meta)")
    ap.add_argument("--meta", type=Path, help="the package's meta.json (its `hot_loop`)")
    ap.add_argument("--trial", type=Path, help="a trial directory: its final.* and the hot loop its "
                                               "trial.json recorded (else the package's meta.json)")
    a = ap.parse_args(list(argv) if argv is not None else None)
    if a.trial:
        rec = json.loads((a.trial / "trial.json").read_text())
        hot = rec.get("hot_loop")
        if hot is None:
            meta = Path(__file__).resolve().parent.parent / "prepared" / str(rec.get("benchmark")) / "meta.json"
            hot = json.loads(meta.read_text()).get("hot_loop") if meta.exists() else None
        final = next(a.trial.glob("final.*"), None)
        if final is None:
            ap.error(f"{a.trial}: no final.* source")
        src = final.read_text()
    elif a.source and a.meta:
        hot = json.loads(a.meta.read_text()).get("hot_loop")
        src = a.source.read_text()
    else:
        ap.error("give SOURCE --meta META, or --trial DIR")
    print(json.dumps(trial_fields(hot, src), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
