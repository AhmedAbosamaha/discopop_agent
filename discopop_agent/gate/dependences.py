"""
Checking a pragma against what DiscoPoP observed
---------------------------------------------------
The property that actually makes `#pragma omp parallel for` legal is not "the
output looked the same" — it is that the loop carries no dependence the clauses
do not account for.  DiscoPoP computes exactly that, and its new Do-All detector
writes down the specific dependences that stopped a loop being parallel
(`explorer/doall_prevented.json`).  This stage reads them back.

It reports; it almost never decides.  That asymmetry is deliberate, because the
evidence is strong in one direction only:

  A DYNAMIC blocker is a dependence DiscoPoP OBSERVED at runtime.  A pragma on
  that loop is contradicted by ground truth, and this is the one verdict allowed
  to fail a patch.

  A STATIC blocker is the analysis being conservative about something it could
  not rule out.  Those are routinely spurious — discharging them is the entire
  point of `--llm-deps` — so a static-only region is recorded and passed.

  No blockers is NOT proof of safety.  It means nothing in the profile
  contradicts the pragma, which is a much weaker claim, and the verdict says so.
  Nothing this stage reports can ever RESCUE a patch another stage failed; it can
  only fail one.

Two files are read, for two different questions.  `doall_prevented.json` answers
"did the detector rule this loop out, and on what evidence" — its
`loop_start`/`loop_end` are real source lines.  `dynamic_dependencies.txt`
answers only "has the profiler ever seen this code at all", which separates a
loop that was analysed and cleared from one written after the profile was taken.
The two read identically in `doall_prevented.json` and mean very different things.

That second question is only answerable because the endpoint resolution in
`evidence/deps.py` was fixed: its endpoints are instruction ids, and the number
after an `@` is callpath state rather than a line, so placing a dependence
requires `instructionID_to_lineID_mapping.txt`.

The honest limitation is scope.  For a Tier-1 pragma this check is close to
tautological: DiscoPoP generated that pragma from this same data, so agreement
is guaranteed and the value is only in recording it.  The case where it would
bite hardest — a pragma the LLM wrote on a loop the LLM also wrote — is the case
where the profile predates the code and has nothing to say, which surfaces as
"no-data".  Turning that into a real answer needs a re-profile (44 s on LULESH),
which is why this stage does not attempt one: it reports the gap instead of
hiding it, and the schedule matrix and sanitizer carry the weight there.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..evidence.blockers import load_prevented_deps
from ..evidence.context import _lineid_line
from ..evidence.deps import _classify_var, _load_dependencies


@dataclass
class DependenceEvidence:
    """What the profile says about parallelizing this region."""
    verdict: str = "unavailable"
    # "contradicted"  an OBSERVED loop-carried dependence blocks it -> hard fail
    # "static-only"   blocked only by conservative static analysis -> recorded
    # "no-blocker"    the profiler has seen this code and the detector recorded
    #                 nothing against it.  NOT a clean bill of health — the
    #                 detector rules out what it can prove, not everything wrong.
    # "no-data"       the profile contains nothing for these lines at all: code
    #                 written after it was taken, which is every loop the LLM
    #                 just wrote.  The stage has no opinion, and says so.
    # "unavailable"   no profile to consult at all
    diagnostic: str = ""
    blockers: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def contradicts(self) -> bool:
        return self.verdict == "contradicted"


def _describe(b: Dict[str, Any]) -> str:
    """One blocker, in the terms a reader of the diagnostic will recognise.

    `dep_type` arrives as a repr like "DepType.RAW", and the variable as
    DiscoPoP's internal `GEPRESULT_<array>` spelling; both are normalised here.
    Source and sink lines are frequently absent from these records, so the loop
    range is used rather than printing a placeholder line number.
    """
    dtype = str(b.get("dep_type", "?")).rsplit(".", 1)[-1]
    var, _kind = _classify_var(str(b.get("var_name") or "?"))
    src, snk = _lineid_line(str(b.get("source_line", ""))), _lineid_line(str(b.get("sink_line", "")))
    if src > 0 or snk > 0:
        return f"{dtype} on {var} (line {snk} <- {src})"
    lo, hi = b.get("loop_start"), b.get("loop_end")
    where = f" in the loop at line {lo}" if lo == hi and lo is not None else (
        f" in the loop at lines {lo}-{hi}" if lo is not None else "")
    return f"{dtype} on {var}{where}"


def dependence_evidence(
    discopop_dir: Optional[str], file_id: Optional[int],
    start_line: Optional[int], end_line: Optional[int],
) -> DependenceEvidence:
    """Consult the profile about [start_line, end_line] of `file_id`.

    Every argument is optional because callers that cannot say which region a
    diff targets should get "unavailable" rather than a wrong answer.
    """
    if (discopop_dir is None or file_id is None
            or start_line is None or end_line is None):
        return DependenceEvidence(
            verdict="unavailable",
            diagnostic="caller did not identify a profiled region for this patch")

    dp = Path(discopop_dir)
    if not (dp / "explorer" / "doall_prevented.json").exists():
        return DependenceEvidence(
            verdict="unavailable",
            diagnostic="explorer/doall_prevented.json absent (older explorer, or no profile)")

    blockers = load_prevented_deps(dp, file_id, start_line, end_line)
    observed = [b for b in blockers if "DYNAMIC" in str(b.get("origin", "")).upper()]
    static = [b for b in blockers if "DYNAMIC" not in str(b.get("origin", "")).upper()]

    if observed:
        shown = "; ".join(_describe(b) for b in observed[:3])
        more = f" (+{len(observed) - 3} more)" if len(observed) > 3 else ""
        return DependenceEvidence(
            verdict="contradicted", blockers=observed,
            diagnostic=(
                f"DiscoPoP OBSERVED {len(observed)} loop-carried dependence(s) in "
                f"lines {start_line}-{end_line} that prevent a Do-All: {shown}{more}. "
                f"These were seen at runtime, not inferred, so a parallel-for over "
                f"this loop contradicts measured behaviour."
            ))

    if static:
        shown = "; ".join(_describe(b) for b in static[:3])
        return DependenceEvidence(
            verdict="static-only", blockers=static,
            diagnostic=(
                f"{len(static)} STATIC blocker(s) only, never observed at runtime "
                f"({shown}) — conservative analysis, not evidence of a real "
                f"dependence; not failing on it"
            ))

    raw, war, waw = _load_dependencies(dp / "profiler", start_line, end_line)
    if not (raw or war or waw):
        return DependenceEvidence(
            verdict="no-data",
            diagnostic=(
                f"the profile holds no dependence at all for lines "
                f"{start_line}-{end_line} — code written after the profile was "
                f"taken. This stage has nothing to say about it; the sanitizer "
                f"and the schedule matrix carry this patch"
            ))
    return DependenceEvidence(
        verdict="no-blocker",
        diagnostic=(
            f"the profiler covered lines {start_line}-{end_line} "
            f"({len(raw)} RAW, {len(war)} WAR, {len(waw)} WAW observed) and the "
            f"Do-All detector recorded no blocker. Not proof the pragma is safe "
            f"— the detector rules out what it can prove — so this neither "
            f"passes nor fails the patch on its own"
        ))
