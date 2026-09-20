"""Fix 85, part 2 — when the model and DiscoPoP both annotate the same loop, measure both.

The deferral rule works: a loop DiscoPoP can already parallelize is left to Phase B.  But a
LARGER region containing that loop — a function with no pattern of its own — still goes to the
model, and under ``--llm-pragmas`` the model annotates the inner loops from inside its rewrite.
Phase B then re-profiles, finds the loops already annotated, reports "no applicable pattern",
and DiscoPoP's own pragma is never built, never timed, never seen.

Measured over the archived runs: 22 trials end with a deferred DiscoPoP pattern and only
model-written pragmas.  Displacement is not uniformly good or bad — on PolyBench ``lu`` the
model's pragmas give 2.6–2.8x where DiscoPoP's give 0.21x; on ``jacobi-2d`` they give 2.5x
where DiscoPoP's give 5.9x.  So this module does not pick a side.  For each collision it
builds DiscoPoP's pragma as an alternative, puts it through the same gate, times the two
against each other, and keeps the faster.  The loser is recorded either way, which is the
data E3 would otherwise have to produce separately: who writes the better pragma here, the
model or the analysis tool?

Arbitration needs a measurement, so it runs only where the run already measures
(``--require-speedup``).  With the check off the collision is reported and left alone.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .parse import _LOOP_HEAD_RE, _PRAGMA_LINE_RE


def _loop_header_at(text: str, line: int) -> Optional[str]:
    """The loop header DiscoPoP's pattern names, from the source it was found in.

    `line` is 1-based and comes from `patterns.json`. Clang reports a loop at its `for`
    line, but a pattern occasionally points at the line above; one line of slack covers
    that without matching an unrelated loop.
    """
    lines = text.splitlines()
    for i in (line - 1, line, line - 2):
        if 0 <= i < len(lines) and _LOOP_HEAD_RE.match(lines[i]):
            return lines[i].strip()
    return None


def _pragma_on(text: str, header: str) -> Optional[Tuple[int, int, str]]:
    """Where `header`'s loop carries a pragma in `text`: (pragma index, header index, pragma).

    None when the loop is not found or carries no pragma. Where the same header occurs more
    than once, the annotated one is taken — this asks whether SOME copy of it was annotated.
    """
    lines = text.splitlines()
    for i, l in enumerate(lines):
        if l.strip() != header.strip() or i == 0:
            continue
        j = i - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        if j >= 0 and _PRAGMA_LINE_RE.match(lines[j]):
            return j, i, lines[j]
    return None


def _discopop_pragma(indent: str, kind: str, clauses: str) -> str:
    """DiscoPoP's pragma for a claimed loop, as its patch generator writes it."""
    tail = f" {clauses}".rstrip() if clauses else ""
    return f"{indent}#pragma omp parallel for{tail}"


def collisions(original_text: str, final_text: str,
               inner_patterns: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Loops DiscoPoP claimed that now carry a DIFFERENT, model-written pragma.

    `inner_patterns` is the evidence package's list for the region (line numbers in
    `original_text`). Loops are matched by header text, not by line: the rewrite has moved
    them. A pragma identical to DiscoPoP's is no collision — there is nothing to arbitrate.
    """
    out: List[Dict[str, Any]] = []
    for p in inner_patterns:
        try:
            line = int(p["line"])
        except (KeyError, TypeError, ValueError):
            continue
        header = _loop_header_at(original_text, line)
        if header is None:
            continue
        found = _pragma_on(final_text, header)
        if found is None:
            continue                      # the model left this loop to Phase B, as asked
        pragma_idx, _header_idx, model_pragma = found
        indent = model_pragma[:len(model_pragma) - len(model_pragma.lstrip())]
        dp_pragma = _discopop_pragma(indent, str(p.get("kind", "do_all")),
                                     str(p.get("clauses", "")))
        if " ".join(model_pragma.split()) == " ".join(dp_pragma.split()):
            continue                      # same pragma, whoever wrote it
        out.append({"line": line, "header": header, "pragma_index": pragma_idx,
                    "model_pragma": model_pragma, "discopop_pragma": dp_pragma,
                    "kind": p.get("kind"), "clauses": p.get("clauses", "")})
    return out


def swap(final_text: str, collision: Dict[str, Any]) -> str:
    """`final_text` with this loop carrying DiscoPoP's pragma instead of the model's."""
    lines = final_text.splitlines()
    lines[int(collision["pragma_index"])] = str(collision["discopop_pragma"])
    return "\n".join(lines) + ("\n" if final_text.endswith("\n") else "")


def arbitrate(
    final_text: str,
    original_text: str,
    inner_patterns: List[Dict[str, Any]],
    source_file: str,
    validate_alternative: Any,
    measure: Any,
    min_ratio: float = 1.1,
    log: Any = print,
) -> Tuple[str, List[Dict[str, Any]]]:
    """Keep, for every collision, whichever of the two pragmas measures faster.

    `validate_alternative(text) -> (ok, diagnostic)` must put the alternative through the
    same gate the model's rewrite passed — DiscoPoP's clauses are not assumed correct.
    `measure(before_text, after_text) -> (ok, ratio, diagnostic)` returns before/after, so a
    ratio above 1 means `after` is faster (the signature of `gate.timing.measure_marginal`).

    Returns the text to keep and one record per collision, whichever side wins. A collision
    is decided only outside the noise band [1/min_ratio, min_ratio]; inside it the model's
    pragma stands, because nothing was shown.
    """
    found = collisions(original_text, final_text, inner_patterns)
    records: List[Dict[str, Any]] = []
    text = final_text
    for c in found:
        rec: Dict[str, Any] = {k: c[k] for k in ("line", "header", "model_pragma", "discopop_pragma")}
        log(f"│  [Fix 85] both annotate the loop at line {c['line']}: "
            f"model {c['model_pragma'].strip()!r} vs DiscoPoP {c['discopop_pragma'].strip()!r}")
        alt = swap(text, c)
        ok, diag = validate_alternative(alt)
        if not ok:
            rec.update(winner="model", reason="discopop_alternative_rejected", diagnostic=diag[:400])
            log(f"│  [Fix 85] DiscoPoP's does not pass the gate ({diag[:60]}) — keeping the model's")
            records.append(rec)
            continue
        ok_m, ratio, mdiag = measure(alt, text)     # >1 : the model's text is faster
        if not ok_m or not ratio:
            rec.update(winner="model", reason="not_measurable", diagnostic=mdiag[:400])
            log(f"│  [Fix 85] could not time the two ({mdiag[:60]}) — keeping the model's")
            records.append(rec)
            continue
        rec["ratio_model_over_discopop"] = round(ratio, 3)
        if ratio <= 1.0 / min_ratio:
            text = alt
            rec.update(winner="discopop", reason="faster")
            log(f"│  [Fix 85] DiscoPoP's pragma is {1 / ratio:.2f}x faster — taking it")
        elif ratio >= min_ratio:
            rec.update(winner="model", reason="faster")
            log(f"│  [Fix 85] the model's pragma is {ratio:.2f}x faster — keeping it")
        else:
            rec.update(winner="model", reason="within_noise")
            log(f"│  [Fix 85] the two are within {min_ratio:.2f}x ({ratio:.2f}x) — keeping the model's")
        records.append(rec)
    return text, records
