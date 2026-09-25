"""The lines a benchmark shares with its measurement harness (Fix 97, D39, 25 Sep 2026)
===================================================================================
From packaging v4 a benchmark's file holds only the benchmark's own code; the measurement
lives in a header outside it. A few lines connect the two — for a TSVC loop the `#include`,
the per-repetition `pb_mix(nl)` call and `PB_MAIN(kernel)` — and they are handed to the agent
as `--protected-line`. A candidate that changes, moves, drops or duplicates one of them
changes what is MEASURED, not what is computed, so it is refused here, before anything is
built — as the stage `harness`, whose retry is not charged to the region's budget: the model's
parallelization is not what failed (E1c class A, `s313`: the agent's model inlined `pb_mix`
into the kernel; the output was identical, the gate kept it, the harness had to discard it).

Every arm is told about these lines in the same words (`llm/request.py:_protected_block`);
this check is the agent's alone — its twins and the model alone have no gate by design.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Sequence

from ..sources import _apply_in_memory


def protected_sequence(text: str, protected: Sequence[str]) -> List[str]:
    """The protected lines of `text`, in order, whitespace-stripped."""
    wanted = set(protected)
    return [ln.strip() for ln in text.splitlines() if ln.strip() in wanted]


def block_enders(text: str, protected: Sequence[str]) -> List[str]:
    """The protected lines that are the LAST statement of their block — followed, after blank
    lines, by a closing brace. `pb_mix(nl);` ends the repetition loop's body: moved to its start
    it keeps its order among the protected lines but perturbs the data before the computation
    instead of after it, which changes what is measured."""
    wanted = set(protected)
    lines = [ln.strip() for ln in text.splitlines()]
    out = []
    for i, ln in enumerate(lines):
        if ln in wanted:
            nxt = next((x for x in lines[i + 1:] if x), "")
            if nxt.startswith("}"):
                out.append(ln)
    return out


def check_protected(diff: str, source_file: str, protected: Sequence[str]) -> Optional[str]:
    """None when the candidate leaves every protected line as it is and where it is (in the
    same order, none dropped, none added); otherwise what changed, in the words the model
    gets back."""
    if not protected:
        return None
    after = _apply_in_memory(diff, source_file)
    if after is None:
        return None                      # the apply stage reports a diff that does not apply
    original = Path(source_file).read_text()
    before = protected_sequence(original, protected)
    now = protected_sequence(after, protected)
    if now == before:
        ends = block_enders(original, protected)
        moved = [l for l in dict.fromkeys(ends) if block_enders(after, protected).count(l) < ends.count(l)]
        if not moved:
            return None
        return ("the candidate moves lines that belong to the program's measurement — "
                + "; ".join(f"`{l}`" for l in moved) + " no longer ends its block. They must stay "
                "exactly as they are and where they are.")
    gone = [l for l in dict.fromkeys(before) if now.count(l) < before.count(l)]
    added = [l for l in dict.fromkeys(now) if now.count(l) > before.count(l)]
    what = []
    if gone:
        what.append("changed or removed: " + "; ".join(f"`{l}`" for l in gone))
    if added:
        what.append("added again: " + "; ".join(f"`{l}`" for l in added))
    if not what:
        what.append("moved: they are no longer in their original order")
    return ("the candidate edits lines that belong to the program's measurement — "
            + ", ".join(what) + ". They must stay exactly as they are and where they are.")
