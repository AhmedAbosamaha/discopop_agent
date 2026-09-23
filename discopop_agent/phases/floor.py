"""
The floor — DiscoPoP's own program, which the agent's may not fall below (D32)
------------------------------------------------------------------------------
Settle asks one speed question: is the finished program slower than the ORIGINAL?  It
never asks whether it is slower than what DiscoPoP alone would have delivered, so
"DiscoPoP + agent" could subtract.  E1's class A showed both ways it does: on `vpvtv`
the model rewrote the loop DiscoPoP already parallelized and the finished program ran
at 2.37× where DiscoPoP's own reached 4.08× (worse); on `s000` the rewrite ended slower
than the original, Settle dropped everything, and DiscoPoP's own 4.03× pragma went with
it (lost).

So before Phase A the agent builds DiscoPoP's own gated program — exactly what the
`discopop_gate` arm delivers: Phase B and Settle on the original, no model — keeps it
as the floor, and puts the original back.  After the final Settle the agent's program
is timed against the floor with the same paired measurement and threshold every other
speed decision uses; if it is slower, DiscoPoP's program is shipped instead.  Where
DiscoPoP alone keeps nothing — every class-R loop of E1 — the floor IS the original and
this is exactly the Settle check that already ran.
"""
from __future__ import annotations

import contextlib
import copy
import json
import statistics
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .. import project as project_mod
from ..args import AgentArguments
from ..gate.timing import measure_marginal, time_source
from ..llm import normalize_code
from ..plan import impact as impact_mod
from .phase_b import SPEED_THRESHOLD_KEY, _phase_b
from .settle import _settle
from .verdicts import _MARGINAL_NOISE


def _differs(a: Dict[str, str], b: Dict[str, str]) -> List[str]:
    return [p for p in a if normalize_code(a[p]) != normalize_code(b.get(p, a[p]))]


def build_floor(
    args: AgentArguments, dp_dir: Path, output_dir: Path, originals: Dict[str, str],
    reference_output: "str | None", reference_outputs: "List[Tuple[List[str], str]] | None",
    binary_args: "List[str] | None", reference_time: "float | None",
    gate_cache: Dict[str, Any], impact: "impact_mod.ImpactModel | None",
) -> "Tuple[Optional[Dict[str, str]], List[Dict[str, Any]]]":
    """DiscoPoP's own gated program for this run, and its accepted records.

    Returns (None, []) when DiscoPoP alone keeps nothing — the floor is then the original,
    which Settle already guards.  Its console goes to `<output>/floor/floor.log`, so the
    run's own log (and every counter the harness reads from it) describes the agent's run.
    """
    focus = args.source_file
    floor_dir = output_dir / "floor"
    floor_dir.mkdir(parents=True, exist_ok=True)
    floor_log: List[Any] = []
    survivors: List[Any] = []
    kept: List[Dict[str, Any]] = []
    with open(floor_dir / "floor.log", "w") as fh, contextlib.redirect_stdout(fh):
        kept = _phase_b(args, dp_dir, floor_dir, reference_output, reference_outputs, binary_args,
                        reference_time, gate_cache, floor_log, copy.deepcopy(impact))
        if floor_log:
            survivors, _notes = _settle(originals, floor_log, args, floor_dir, reference_output,
                                        reference_outputs, binary_args, reference_time,
                                        speed_threshold=gate_cache.get(SPEED_THRESHOLD_KEY, _MARGINAL_NOISE))
    texts = {p: Path(p).read_text() for p in originals}
    for p, t in originals.items():                 # the agent itself starts from the original
        if Path(p).read_text() != t:
            Path(p).write_text(t)
    project_mod.work_on(args, focus)
    if not _differs(originals, texts):
        print("  [floor] DiscoPoP alone keeps nothing — the floor is the original program (D32)\n")
        return None, []
    kept_ids = {rid for c in survivors if c["kind"] == "pragma"
                for rid in (c.get("region_ids") or [c["region_id"]])}
    accepted = [r for r in kept if r.get("phase") == "B" and r["region_id"] in kept_ids]
    print(f"  [floor] DiscoPoP alone keeps {len(accepted)} pragma(s) — the agent's program must not be "
          f"slower than that one (D32; details in floor/floor.log)\n")
    (floor_dir / "floor_accepted.json").write_text(json.dumps(accepted, indent=2))
    return texts, accepted


def _measure_states(a: Dict[str, str], b: Dict[str, str], args: AgentArguments,
                    binary_args: "List[str] | None", pairs: int = 5) -> Tuple[bool, float, str]:
    """time(a) / time(b), paired and interleaved like every speed decision of the agent.

    One differing file: the agent's own `measure_marginal`.  Several (a project where the
    two programs differ in more than one unit): each side's OTHER files are written to
    disk before that side is timed, since a project build stages every unit but the focus
    from disk.  The disk is left holding `b`."""
    differ = _differs(a, b)
    if not differ:
        return True, 1.0, ""
    focus = str(Path(args.source_file).resolve())
    target = focus if focus in differ else differ[0]
    project_mod.work_on(args, target)
    flags = list(args.timing_cflags) or None
    if len(differ) == 1:
        return measure_marginal(a[target], b[target], target, binary_args, pairs=pairs, extra_flags=flags)
    ratios: List[float] = []
    with tempfile.TemporaryDirectory(prefix="dp_agent_floor_") as tmp:
        work = Path(tmp)
        for i in range(pairs):
            times = []
            for side, state in (("floor", a), ("agent", b)):
                for p in differ:
                    if p != target:
                        Path(p).write_text(state[p])
                ok, t, _out, diag = time_source(state[target], target, work, f"{side}{i}", binary_args,
                                                repeats=1, extra_flags=flags)
                if not ok:
                    return False, 0.0, diag
                times.append(t)
            if times[1] > 0:
                ratios.append(times[0] / times[1])
    return (True, statistics.median(ratios), "") if ratios else (False, 0.0, "no valid timing samples")


def apply_floor(
    args: AgentArguments, originals: Dict[str, str], floor_texts: Dict[str, str],
    floor_accepted: List[Dict[str, Any]], accepted: List[Dict[str, Any]],
    binary_args: "List[str] | None", gate_cache: Dict[str, Any], output_dir: Path,
) -> List[Dict[str, Any]]:
    """Keep the agent's finished program unless it is slower than the floor; then ship the floor.

    Returns the accepted records that describe what is on disk afterwards."""
    focus = args.source_file
    try:
        return _decide(args, originals, floor_texts, floor_accepted, accepted, binary_args,
                       gate_cache, output_dir)
    finally:
        project_mod.work_on(args, focus)


def _decide(
    args: AgentArguments, originals: Dict[str, str], floor_texts: Dict[str, str],
    floor_accepted: List[Dict[str, Any]], accepted: List[Dict[str, Any]],
    binary_args: "List[str] | None", gate_cache: Dict[str, Any], output_dir: Path,
) -> List[Dict[str, Any]]:
    final = {p: Path(p).read_text() for p in originals}
    if not _differs(floor_texts, final):
        print("  [floor] the finished program is DiscoPoP's own (D32)\n")
        return accepted
    threshold = gate_cache.get(SPEED_THRESHOLD_KEY, _MARGINAL_NOISE)
    ok, ratio, diag = _measure_states(floor_texts, final, args, binary_args)
    for p, t in final.items():                     # leave the agent's program on disk while deciding
        if Path(p).read_text() != t:
            Path(p).write_text(t)
    if ok and ratio >= threshold:
        print(f"  [floor] kept the agent's program — {ratio:.2f}× DiscoPoP's own, paired "
              f"(kept at or above {threshold:.3f}; D32)\n")
        return accepted
    for p, t in floor_texts.items():
        Path(p).write_text(t)
    why = f"{ratio:.2f}× DiscoPoP's own, paired" if ok else f"not measurable against it ({diag[:60]})"
    print(f"  [floor] shipped DiscoPoP's own program (D32) — the agent's was {why}\n")
    (output_dir / "accepted.json").write_text(json.dumps(floor_accepted, indent=2))
    return list(floor_accepted)
