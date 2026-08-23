"""
DiscoPoP's own account of why a loop is not a Do-All
------------------------------------------------------
`doall_prevented.json` is written by the new Do-All detector and names the exact
dependences that blocked it, each tagged with its origin: STATIC (a dependence
the analysis could not rule out) or DYNAMIC (one it actually observed).

That distinction is load-bearing.  A dynamic blocker is ground truth; a static
one is an over-approximation that may not occur at all, and is the only kind the
dependence review is ever allowed to discharge.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .context import _lineid_line


def load_prevented_deps(
    discopop_dir: Path, file_id: int, start_line: int, end_line: int
) -> List[dict]:
    """Load the Do-All blockers DiscoPoP's new detector recorded for this region.

    Reads explorer/doall_prevented.json (written by new_do_all_detector) and
    returns entries whose loop overlaps [start_line, end_line] in the same file,
    or whose blocking dependency's source/sink line falls inside the region.
    Returns [] if the file is absent (e.g. old explorer) or nothing matches.
    """
    import json

    f = discopop_dir / "explorer" / "doall_prevented.json"
    if not f.exists():
        return []
    try:
        records = json.loads(f.read_text())
    except (OSError, ValueError):
        return []

    matched: List[dict] = []
    for rec in records:
        lf = rec.get("loop_file")
        ls, le = rec.get("loop_start"), rec.get("loop_end")
        loop_overlaps = (
            lf == file_id and ls is not None and le is not None
            and not (le < start_line or ls > end_line)
        )
        src_ln, snk_ln = _lineid_line(rec.get("source_line", "")), _lineid_line(rec.get("sink_line", ""))
        dep_in_region = (start_line <= src_ln <= end_line) or (start_line <= snk_ln <= end_line)
        if loop_overlaps or dep_in_region:
            matched.append(rec)
    return matched


def _var_classification(pattern: Optional[dict]) -> dict:
    """Pull DiscoPoP's OpenMP data-sharing classification out of a detected
    pattern (a patterns.json entry, carried on the candidate).

    Returns a dict with lists for shared / private / first_private / last_private
    / reduction.  Empty ({}) when no pattern was detected for the region, in which
    case DiscoPoP has no classification to offer.  Pattern entries may be plain
    variable-name strings or dicts carrying a 'name' field; both are handled.
    """
    if not pattern:
        return {}

    def _names(key: str) -> List[str]:
        out: List[str] = []
        for v in pattern.get(key) or []:
            out.append(str(v.get("name", v)) if isinstance(v, dict) else str(v))
        return out

    return {
        "shared": _names("shared"),
        "private": _names("private"),
        "first_private": _names("first_private"),
        "last_private": _names("last_private"),
        "reduction": _names("reduction"),
    }
