"""Did a rewrite touch the packaging's own code?

Every packaged benchmark carries scaffolding that the harness relies on and that is not
part of the computation under study: the digest (`pb_emit`, `pb_report`, `pb_newline`),
the perturbed-input machinery (`pb_seed`, `pb_uniform`, `PB_PERTURB`) and the timed
region (`pb_timer_start`, `pb_timer_stop`). The agent is free to rewrite the program, and
the gate checks the rewrite's output — but an edit to the scaffolding changes the
instrument, not the program:

* moving `pb_timer_stop` earlier shrinks the timed region and reports a speedup that
  does not exist;
* rewriting `PB_PERTURB` changes the input the perturbed check runs on;
* rewriting the digest changes what "same output" means.

The first server pilot with working model calls (`pilot2`) kept exactly such a rewrite: the
model expanded `PB_PERTURB` in `main` and parallelised it. It passed every check and saved
no time, but it counted as a parallelisation. This module finds such edits by comparing the
original and final source; the harness gives an affected trial its own outcome.

Three checks, all on comment-free text with whitespace normalised:

1. every scaffolding DEFINITION (a `pb_*`/`PB_*` function or macro) is unchanged;
2. the ordered list of lines USING scaffolding outside those definitions is unchanged —
   nothing removed, added, edited or reordered;
3. the timed region still covers what it covered. Every line the rewrite left unchanged
   (matched by a line diff) must lie on the same side of the timer boundary as before, so
   moving `pb_timer_start`/`pb_timer_stop` — which leaves their own text, and therefore
   check 2, untouched — is caught by the code it pushes out of the region. Lines the
   rewrite changed are not compared, which is what lets a model restructure the loops
   inside a region that IS the computation (`md`, `pathfinder`, NPB). A region that wraps
   only a call (PolyBench, `hotspot`, `nw`) may change, but only in one direction: the
   computation may move INTO it (the model inlining the kernel, as seen in `local_obs1`), so
   afterwards it must still contain a loop, and no new loop may appear in the same function
   outside it (computation moved OUT of the timer).
"""
from __future__ import annotations

import difflib
import re
from typing import Dict, List, Sequence, Tuple

# `\b` before the prefix keeps PolyBench's own `_PB_NI` bound macros out.
TOKEN = re.compile(r"\b(?:pb|PB)_[A-Za-z0-9_]+\b")
_DEFINE = re.compile(r"^\s*#\s*define\s+((?:pb|PB)_[A-Za-z0-9_]+)")
_FUNC = re.compile(r"^\s*(?:static\s+)?(?:inline\s+)?[A-Za-z_][\w\s\*]*?\b((?:pb|PB)_[A-Za-z0-9_]+)\s*\([^;]*$")
_LOOP = re.compile(r"\b(?:for|while|do)\b")
_START = re.compile(r"\bpb_timer_start\s*\(")
_STOP = re.compile(r"\bpb_timer_stop\s*\(")


def _strip_comments(text: str) -> str:
    """Remove comments, keeping line numbers (each removed newline is put back).

    String literals are skipped so a `//` inside one is not taken for a comment."""
    out: List[str] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c in "\"'":
            j = i + 1
            while j < n and text[j] != c:
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        elif text.startswith("//", i):
            j = text.find("\n", i)
            i = n if j < 0 else j
        elif text.startswith("/*", i):
            j = text.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("\n" * text.count("\n", i, j))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _norm(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def _analyse(text: str) -> Tuple[List[Tuple[str, str]], List[str], List[List[str]],
                                  List[str], List[bool]]:
    """(definitions, uses outside definitions, timed windows, normalised lines,
    whether each line lies inside a timed window) of one source."""
    lines = _strip_comments(text).splitlines()
    defs: List[Tuple[str, str]] = []
    in_def = [False] * len(lines)
    i = 0
    while i < len(lines):
        m = _DEFINE.match(lines[i])
        if m:
            j = i
            while lines[j].rstrip().endswith("\\") and j + 1 < len(lines):
                j += 1
            body = " ".join(_norm(x.rstrip().rstrip("\\")) for x in lines[i:j + 1])
            defs.append((m.group(1), _norm(body)))
            for k in range(i, j + 1):
                in_def[k] = True
            i = j + 1
            continue
        m = _FUNC.match(lines[i])
        if m and "{" in "".join(lines[i:i + 3]):
            depth, seen, j = 0, False, i
            while j < len(lines):
                depth += lines[j].count("{") - lines[j].count("}")
                seen = seen or "{" in lines[j]
                if seen and depth <= 0:
                    break
                j += 1
            j = min(j, len(lines) - 1)
            defs.append((m.group(1), " ".join(_norm(x) for x in lines[i:j + 1] if x.strip())))
            for k in range(i, j + 1):
                in_def[k] = True
            i = j + 1
            continue
        i += 1

    uses = [_norm(lines[k]) for k in range(len(lines))
            if not in_def[k] and TOKEN.search(lines[k])]

    windows: List[List[str]] = []
    inside = [False] * len(lines)
    k = 0
    while k < len(lines):
        if not in_def[k] and _START.search(lines[k]):
            j = k + 1
            while j < len(lines) and not (not in_def[j] and _STOP.search(lines[j])):
                j += 1
            windows.append([_norm(x) for x in lines[k + 1:j] if x.strip()])
            for idx in range(k + 1, min(j, len(lines))):
                inside[idx] = True
            k = j
        k += 1
    return defs, uses, windows, [_norm(x) for x in lines], inside


def _runs(flags: List[bool]) -> List[Tuple[int, int]]:
    """(first, last) index of each run of True, in order."""
    out: List[Tuple[int, int]] = []
    k = 0
    while k < len(flags):
        if flags[k]:
            j = k
            while j + 1 < len(flags) and flags[j + 1]:
                j += 1
            out.append((k, j))
            k = j + 1
        else:
            k += 1
    return out


def _top_block(lines: List[str], k: int) -> Tuple[int, int]:
    """(first, last) index of the top-level brace block (the function) containing line k."""
    depth = 0
    start_of_block = 0
    before: List[int] = []
    for i, x in enumerate(lines):
        before.append(depth)
        if depth == 0 and "{" in x:
            start_of_block = i
        depth += x.count("{") - x.count("}")
        if i >= k and depth <= 0 and before[k] > 0:
            # find where this block began: the last depth-0 line at or before k that opened it
            lo = k
            while lo > 0 and before[lo] > 0:
                lo -= 1
            return lo, i
    return start_of_block, len(lines) - 1


def _block_enders(text: str, protected: Sequence[str]) -> List[str]:
    """Protected lines that end their block (next non-blank line is a closing brace) — the same
    rule as the agent's gate (`gate/harness_lines.py`)."""
    wanted = set(protected)
    lines = [ln.strip() for ln in text.splitlines()]
    return [ln for i, ln in enumerate(lines)
            if ln in wanted and next((x for x in lines[i + 1:] if x), "").startswith("}")]


def _protected_seq(text: str, protected: Sequence[str]) -> List[str]:
    wanted = set(protected)
    return [ln.strip() for ln in text.splitlines() if ln.strip() in wanted]


def check(original: str, final: str, protected: Sequence[str] = ()) -> Dict[str, object]:
    """Compare the scaffolding of two versions of one packaged source.

    ``protected`` (packaging v4, D39): the lines the package's meta.json lists as shared with
    the measurement harness, which now lives outside the file — the ``#include`` among them,
    which uses no ``pb_`` name and so is invisible to the three checks below. Each must still
    be there, unchanged, in the same order (the agent's gate applies the same rule, Fix 97).

    Returns ``{"ok": bool, "problems": [str, ...], "applies": bool}``. ``applies`` is
    False for a source with no scaffolding at all (nothing to protect)."""
    d0, u0, w0, l0, in0 = _analyse(original)
    d1, u1, w1, l1, in1 = _analyse(final)
    problems: List[str] = []
    if protected:
        p0, p1 = _protected_seq(original, protected), _protected_seq(final, protected)
        if p0 != p1:
            gone = [x for x in dict.fromkeys(p0) if p1.count(x) < p0.count(x)]
            extra = [x for x in dict.fromkeys(p1) if p1.count(x) > p0.count(x)]
            problems += [f"protected line removed or edited: {x[:100]}" for x in gone]
            problems += [f"protected line added: {x[:100]}" for x in extra]
            if not gone and not extra:
                problems.append("protected lines were reordered")
        else:
            e0, e1 = _block_enders(original, protected), _block_enders(final, protected)
            problems += [f"protected line moved (no longer ends its block): {x[:100]}"
                         for x in dict.fromkeys(e0) if e1.count(x) < e0.count(x)]
    if not d0 and not u0:
        return {"ok": not problems, "problems": problems, "applies": bool(protected)}

    names0 = [n for n, _ in d0]
    if names0 != [n for n, _ in d1]:
        problems.append(f"scaffolding definitions changed: {names0} -> {[n for n, _ in d1]}")
    else:
        for (name, b0), (_, b1) in zip(d0, d1):
            if b0 != b1:
                problems.append(f"definition of {name} was edited")

    if u0 != u1:
        removed = [x for x in u0 if x not in u1]
        added = [x for x in u1 if x not in u0]
        if not removed and not added:
            problems.append("scaffolding calls were reordered")
        for x in removed[:5]:
            problems.append(f"scaffolding line removed or edited: {x[:100]}")
        for x in added[:5]:
            problems.append(f"scaffolding line added: {x[:100]}")

    sm = difflib.SequenceMatcher(None, l0, l1, autojunk=False)
    matched_final = {b + off for _a, b, size in sm.get_matching_blocks() for off in range(size)}
    if len(w0) != len(w1):
        problems.append(f"timed regions: {len(w0)} in the original, {len(w1)} in the final")
    else:
        spans = _runs(in1)
        for n, (a, b) in enumerate(zip(w0, w1)):
            call_only = not any(_LOOP.search(x) for x in a)
            if not call_only or a == b:
                continue
            if not any(_LOOP.search(x) for x in b):
                problems.append(f"timed region {n + 1} lost its computation: {a[:2]} -> {b[:2]}")
                continue
            if n < len(spans):
                lo, hi = _top_block(l1, spans[n][0])
                moved_out = [l1[k] for k in range(lo, hi + 1)
                             if k not in matched_final and not in1[k] and _LOOP.search(l1[k])]
                if moved_out:
                    problems.append(f"timed region {n + 1} changed and a new loop appeared outside it "
                                    f"in the same function: {moved_out[0][:80]}")
    crossed = []
    for blk in sm.get_matching_blocks():
        for off in range(blk.size):
            line = l0[blk.a + off]
            # Lines with no identifier (`}`, `{`) pair up anywhere and prove nothing.
            if (re.search(r"[A-Za-z0-9]", line) and in0[blk.a + off] != in1[blk.b + off]
                    and not TOKEN.search(line)):
                crossed.append((line, in0[blk.a + off]))
    if crossed:
        out = sum(1 for _, was_in in crossed if was_in)
        problems.append(f"timed region boundary moved: {out} unchanged line(s) left the region, "
                        f"{len(crossed) - out} entered it (first: {crossed[0][0][:80]})")
    return {"ok": not problems, "problems": problems, "applies": True}
