"""
The matched model-only twin (D38): an agent arm, minus the gate
----------------------------------------------------------------
Every experiment compares agent arms that differ in one thing (evidence, who writes the
pragmas, depth, ranking).  The twin answers, for each of those arms, what the SAME model
does with the SAME DiscoPoP information when nothing checks its work.  It takes the agent
arm's own arguments (parsed by the agent's own parser) and runs the agent's own code for
everything that is DiscoPoP's — the start-up measurements, the ranked queue, the region,
the evidence, the request — and nothing that is the gate's:

  * the model gets the request the agent's model gets for the same region, built by the
    agent's own `_build_direct_prompt` from the same profile; the system prompt is the
    agent's own blocks with the gate's checks described as what judges the FINISHED
    program, and the clause and sentence that promise feedback removed (see `_system`);
  * one attempt per region, no feedback, no format re-prompt; what the model leaves in
    the file stays in the file — nothing is compiled, run, raced, timed or reverted here;
  * after an edit the program is re-profiled, as the agent re-profiles a kept rewrite, so
    the rest of the queue is read from a profile that describes the file, and regions the
    rewrite created join the queue at depth+1 up to `--restructure-depth`;
  * at the end DiscoPoP annotates, as the agent's Phase B does, from the final profile:
    every applicable pattern, re-derived against the file as it stands, with DiscoPoP's
    fixed clause repair (Fix 91) — skipping only what is structural (a loop already
    annotated, a loop nested in a parallel one).  No clause check, no TSan, no schedules,
    no speed check, no joint judgement (D33), no Settle, no floor (D32).

The harness judges the finished program exactly as it judges the agent's, and the race
check (`race_check.py`) is run on every twin's programs.  `twin_model_program.*` in the
output directory is the program before DiscoPoP annotated it, so the model's share and
DiscoPoP's unchecked share of a twin's result can be told apart afterwards.

    python -m discopop_agent.twin <the agent arm's own arguments>

With `--budget 0` (the twin of `discopop_gate`) no model is called: that is DiscoPoP's
own program with nothing checked — the corner the gate's value on DiscoPoP is read from.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

from . import project as project_mod
from .args import AgentArguments, parse_args
from .evidence import assemble
from .gate import numerical_noise_floor
from .llm.prompts import (_ASK, _ASK_ANNOTATE, _CONTRACT_NO_PRAGMA, _CONTRACT_PRAGMA,
                          _GIVEN_ITEMS, _OMP_RULES, _OUTPUT_DIRECT, _PRAGMA_FORMS, _ROLE,
                          _ROLE_ANNOTATE, _RULE, _contract, _granularity, _how_compared, _wrap)
from .llm.providers import _complete, _make_client, _sync_workspace, _workspace_diff
from .llm.request import _build_direct_prompt
from .plan import build_candidates, region_budget, region_fingerprint
from .plan import impact as impact_mod
from .pragmas import (_already_annotated, _read_tier1_patch, _repair_pragma_clauses,
                      derive_pragma_patch, existing_parallel_spans)
from .profiling import _measure_hotspots, _reprofil
from .sources import _apply_to_source
from .types import GateFacts

# The agent's reason a Tier-2 region reaches the model on its first attempt (phase_a.py).
FIRST_REASON = "DiscoPoP found no applicable parallelism pattern for this region"


# ---------------------------------------------------------------------------
# The prompt: the agent's own blocks, the gate as what judges the finished program
# ---------------------------------------------------------------------------
# Exactly these texts of the agent's differ, and each names the gate during the run or
# feedback.  test_features.py (twin-prompt) asserts that nothing else does.
FEEDBACK_CLAUSE = "after a failed attempt, which check failed and why"
EARLIER_TURN = ("  If you\nedited this file on an earlier turn those edits are still there: build on\n"
                "them or replace them, but never restore the original code.")
SPEED_ONE_THREAD = ("runs faster than the same build on one thread",
                    "runs faster than the original sequential program")
SPEED_GOAL_ANNOTATE = (", and is measurably faster than the same build held to one thread",
                       ", and is measurably faster than the original sequential program")


def _given(include: "Set[str] | None") -> str:
    """prompts._given, less the clause that promises feedback after a failed attempt."""
    items = [text for name, text in _GIVEN_ITEMS if include is None or name in include]
    head = _RULE + "WHAT WE GIVE YOU\n" + _RULE
    if not items:
        return (head + _wrap(
            "Every request carries the region's source.  No profiling data is provided for "
            "this region: work from the code itself.") + "\n\n")
    body = _wrap("Every request carries the region's source and, from the profile: "
                 + ", ".join(items) + ".")
    advice = "Work from that evidence rather than from what the algorithm is called."
    if include is None or "deps" in include:
        advice = _wrap(
            "Work from that evidence rather than from what the algorithm is called.  Two "
            "things in it are easy to misread on inspection: WAR and WAW usually mean a "
            "location is reused, not that a value travels between iterations; and a "
            "dependence on a loop's own counter is never the blocker, because "
            "privatising the counter removes it.")
    return head + body + "\n\n" + advice + "\n\n"


def _judged_steps(gate: GateFacts) -> List[str]:
    """What judges the finished program: the harness's verification and, afterwards, the
    gate's race stages (race_check.py).  The static clause check is the gate's alone."""
    steps = ["it must compile, plain and again with -fopenmp",
             "ThreadSanitizer runs the parallel build: any real race fails it"]
    if gate.stress:
        steps.append("the parallel build is run repeatedly at one thread count, then at\n"
                     "     other thread counts and under static, dynamic and guided schedules:\n"
                     "     every run has to agree with the others")
    steps.append(_how_compared(gate))
    if gate.require_speedup:
        steps.append("it is timed at several thread counts against the original sequential\n"
                     "     program, and has to be faster")
    return steps


def _judged(gate: GateFacts, llm_pragmas: bool) -> str:
    """The agent's "HOW YOUR REWRITE IS CHECKED" (prompts._checked / _checked_annotate), as
    what judges the program once the model is done."""
    if "gate" in gate.omit:
        return ""
    steps = _judged_steps(gate)
    if not llm_pragmas:
        steps.insert(0, "DiscoPoP re-profiles the program as you leave it and inserts its own\n"
                        "     pragma for every pattern it then finds — nothing is reverted, and a\n"
                        "     loop it finds no pattern in stays sequential")
    body = "\n".join(f"  {i}. {t}" for i, t in enumerate(steps, 1))
    head = (_RULE + "HOW YOUR REWRITE IS JUDGED\n" + _RULE
            + "Nothing checks your work while you do it, and you get one attempt.  When you are\n"
            "done, the program as you leave it is judged:\n" + f"{body}\n\n")
    if llm_pragmas:
        return (head + f"Steps 2-{len(steps)} run your loops with iterations overlapping in arbitrary order.  A\n"
                "loop you marked parallel has to give the same result whatever order its\n"
                "iterations run in — reproducing the output in serial proves nothing about\n"
                "that.  This list is the whole judgement, and a pragma you did not write is a\n"
                "loop that was never parallelized.\n\n"
                + _granularity(gate, len(steps), "annotate"))
    return (head + f"Steps 3-{len(steps)} run the program with iterations overlapping in\n"
            "arbitrary order.  A loop you intend to be parallel has to give the same result\n"
            "whatever order its iterations run in — that, not merely reproducing the output\n"
            "in serial, is what is being asked for.\n\n"
            + _granularity(gate, len(steps), "expose"))


def _system(gate: GateFacts, include: "Set[str] | None", llm_pragmas: bool) -> str:
    """prompts._system_prompt("direct", llm_pragmas, False, gate, include), minus the gate
    during the run and feedback.  --llm-recon's addendum is left out: it serves the fast
    refresh, which the twin does not have (E4 has no twin)."""
    out = _OUTPUT_DIRECT.replace(EARLIER_TURN, "")
    if llm_pragmas:
        goal = SPEED_GOAL_ANNOTATE[1] if gate.require_speedup else ""
        return (_ROLE_ANNOTATE + _ASK_ANNOTATE.replace("{SPEED_GOAL}", goal) + _given(include)
                + _contract(gate, _CONTRACT_PRAGMA) + _judged(gate, True) + _OMP_RULES
                + _PRAGMA_FORMS + out)
    ask = _ASK if gate.require_speedup else _ASK.replace(
        "race-free, output-preserving,\nand faster than the sequential build.",
        "race-free and output-preserving.")
    return (_ROLE + ask + _given(include) + _contract(gate, _CONTRACT_NO_PRAGMA)
            + _judged(gate, False) + _OMP_RULES + out)


def _request(agent_request: str) -> str:
    """The agent's own first request for the region; only the speed clause of its goal
    names the gate's one-thread comparison."""
    return agent_request.replace(*SPEED_ONE_THREAD)


# ---------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------

def _gate_facts(args: AgentArguments) -> GateFacts:
    """The GateFacts the agent builds for its model call (phase_a.py) — `numeric` measured
    the way the agent measures it, so the request's wording is the agent's."""
    if args.numeric_tolerance:
        args.noise_floor = numerical_noise_floor(
            args.source_file, args.reprofil_args or None,
            extra_inputs=args.check_inputs or None).value
    return GateFacts(require_speedup=args.require_speedup,
                     n_inputs=1 + len(args.check_inputs or []),
                     numeric=args.noise_floor > 0.0, stress=args.schedule_stress,
                     omit=tuple(args.prompt_omit or ()),
                     external_evidence=args.external_evidence or "")


def _impact(args: AgentArguments, dp_dir: Path, force: bool = False) -> "impact_mod.ImpactModel":
    impact = impact_mod.ImpactModel(threads=os.cpu_count() or 1)
    if args.hotspots:
        ok, note = _measure_hotspots(args, dp_dir, force=force)
        if not ok:
            print(f"  [warn] hotspot detection unavailable: {note}")
        impact = impact_mod.load_hotspots(dp_dir, threads=os.cpu_count() or 1)
    return impact


def _fp(c: Any) -> Any:
    return region_fingerprint(c.source_file, c.region.start_line, c.region.end_line, c.region.name)


def _annotate(args: AgentArguments, dp_dir: Path, output_dir: Path,
              impact: "impact_mod.ImpactModel") -> int:
    """Phase B without the gate: every applicable pattern of the final profile, outermost
    and largest first, re-derived against the file as it stands."""
    def cands() -> List[Any]:
        return build_candidates(dp_dir, args.source_file, args.lambda_penalty, args.min_workload,
                                impact=impact, min_impact=args.min_impact,
                                min_runtime_share=args.min_runtime_share,
                                exclude_functions=args.exclude_functions)
    todo = [c for c in cands() if c.tier == 1 and c.pattern and c.pattern.get("applicable_pattern")]
    if impact.available:
        todo.sort(key=lambda c: (-(c.impact_seconds or 0.0), -(c.region.end_line - c.region.start_line)))
    else:
        todo.sort(key=lambda c: c.workload_estimate, reverse=True)
    print(f"\n{'='*60}\n  DiscoPoP annotates — {len(todo)} applicable pattern(s), NOTHING CHECKED\n{'='*60}\n")
    spans: List[Tuple[Any, int, int]] = []
    if args.project is None:
        spans = [(None, a, b) for a, b in existing_parallel_spans(Path(args.source_file).read_text())]
    else:
        for fid, path in project_mod.load_file_mapping(dp_dir).items():
            if args.project.contains(path) and path.is_file():
                spans += [(fid, a, b) for a, b in existing_parallel_spans(path.read_text())]
    applied = 0
    for cand in todo:
        project_mod.work_on(args, cand.source_file)
        r = cand.region
        print(f"┌─ {cand.pattern_type or 'pattern'} @ lines {r.start_line}–{r.end_line}  "
              f"(W={cand.workload_estimate:.0f})")
        if cand.workload_estimate < args.min_workload:
            print("└─ SKIPPED (below --min-workload)\n")
            continue
        if any((f is None or f == r.file_id) and a <= r.start_line and r.end_line <= b
               for f, a, b in spans):
            print("└─ SKIPPED (nested in a loop that is already parallel)\n")
            continue
        for ptype, pattern in [(cand.pattern_type, cand.pattern)] + list(cand.alternates):
            pid = (pattern or {}).get("pattern_id", "?")
            diff = _repair_pragma_clauses(derive_pragma_patch(
                _read_tier1_patch(dp_dir / "patch_generator" / str(pid)), args.source_file),
                args.source_file)
            if not diff:
                continue
            if _already_annotated(diff, args.source_file):
                print("└─ SKIPPED (already annotated)\n")
                break
            print(f"│  {(pattern or {}).get('pragma', '')}")
            if _apply_to_source(diff, args.source_file, output_dir, "twin"):
                spans.append((r.file_id, r.start_line, r.end_line))
                applied += 1
                print("└─ INSERTED (unchecked)\n")
            else:
                print("└─ SKIPPED (the patch would not apply)\n")
            break
        else:
            print("└─ SKIPPED (no generated patch on disk)\n")
    return applied


def run(args: AgentArguments) -> int:
    if args.edit_mode != "direct":
        print("  [FATAL] the twin runs in --edit-mode direct only (the campaign's mode)")
        return 2
    dp_dir = Path(args.discopop_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    from .profiling import tools as _profiling_tools
    _profiling_tools.set_explorer_timeout(args.explorer_timeout)
    project_mod.activate(args.project)
    if args.project is not None:
        project_mod.set_focus(args.source_file)

    print("\n" + "=" * 60 + "\n  Model-only twin (D38) — DiscoPoP's information, no gate, one attempt\n" + "=" * 60)
    print(f"  Source         : {args.source_file}")
    print(f"  Model          : {args.model if args.budget > 0 else '— (budget 0: DiscoPoP alone, unchecked)'}")
    print(f"  Pragmas by     : {'the model, then DiscoPoP' if args.llm_pragmas else 'DiscoPoP'}")
    print(f"  Evidence       : {'full' if args.evidence_sections is None else sorted(args.evidence_sections) or 'none'}")
    print(f"  Depth          : {args.restructure_depth}\n")

    gate = _gate_facts(args)
    system = _system(gate, args.evidence_sections, args.llm_pragmas)
    impact = _impact(args, dp_dir)
    ext = Path(args.source_file).suffix

    def cands() -> List[Any]:
        return build_candidates(dp_dir, args.source_file, args.lambda_penalty, args.min_workload,
                                impact=impact, min_impact=args.min_impact,
                                min_runtime_share=args.min_runtime_share,
                                exclude_functions=args.exclude_functions)

    queue: List[Tuple[int, Any]] = [(0, c) for c in cands()]
    seen: Set[Any] = {_fp(c) for _d, c in queue}
    client = _make_client(args.provider, args.api_key, args.api_base) if args.budget > 0 else None
    asked = edited = 0
    profile_ok = True
    i = 0
    while i < len(queue) and profile_ok:
        depth, cand = queue[i]
        i += 1
        project_mod.work_on(args, cand.source_file)
        r = cand.region
        print(f"┌─ [depth={depth}] {r.region_type} {r.region_id} (lines {r.start_line}–{r.end_line})")
        par = existing_parallel_spans(Path(args.source_file).read_text())
        if any(a <= r.start_line and r.end_line <= b for a, b in par):
            print("└─ COVERED (inside a parallel loop)\n")
            continue
        if cand.tier == 1 and cand.pattern and cand.pattern.get("applicable_pattern"):
            print("└─ DISCOPOP'S (annotated at the end)\n")
            continue
        if depth > args.restructure_depth:
            print(f"└─ SKIPPED (depth {depth} > --restructure-depth {args.restructure_depth})\n")
            continue
        top = max((c.runtime_fraction or 0.0) for _d, c in queue)
        if region_budget(args.budget_policy, args.budget, args.budget_min,
                         cand.runtime_fraction, top) <= 0:
            print("└─ SKIPPED (no model budget for this region)\n")
            continue
        evidence = assemble(cand, dp_dir / "profiler", FIRST_REASON)
        key = "twin:" + str(evidence.region_fingerprint or evidence.region_id)
        ws_file, disk = _sync_workspace(key, args.source_file)
        request = _request(_build_direct_prompt(evidence, ws_file, args.evidence_sections,
                                                args.llm_pragmas, gate))
        print(f"│  [twin] Calling {args.model}...")
        asked += 1
        try:
            reply = _complete(args.provider, client, args.model,
                              [{"role": "user", "content": request}], system,
                              session_key=key, workspace=ws_file.parent, stateless=True)
        except Exception as e:                       # noqa: BLE001 - one attempt: say why it failed
            print(f"│  [twin] LLM call failed: {str(e)[:300]}")
            print("└─ NO ANSWER\n")
            continue
        plan = " ".join(reply.split())[:400]
        if plan:
            print(f"│  [twin] the model's plan: {plan}")
        if _workspace_diff(ws_file, args.source_file, disk) is None:
            print("└─ UNCHANGED\n")
            continue
        # The content fingerprints of what is still queued, taken before the file changes —
        # how the agent recognises them in the next profile (phase_a.py).
        old = [(d, _fp(c)) for d, c in queue[i:]]
        Path(args.source_file).write_text(ws_file.read_text())   # no gate: what the model left stays
        edited += 1
        pragmas = sum(1 for ln in ws_file.read_text().splitlines() if ln.lstrip().startswith("#pragma omp"))
        print(f"│  [twin] edited, {pragmas} OpenMP pragma(s) in the file — kept unchecked")
        print("│  [twin] Re-profiling (as the agent does after a kept rewrite)...")
        profile_ok = _reprofil(args.source_file, dp_dir, args.reprofil_args or None)
        if not profile_ok:
            print("│  [twin] the re-profile failed — no profile describes this file: no further "
                  "region is asked and DiscoPoP annotates nothing")
            print("└─ EDITED\n")
            break
        if args.hotspots:
            impact = _impact(args, dp_dir, force=True)
        fresh = cands()
        by_fp: Dict[Any, List[Any]] = {}
        for c in fresh:
            by_fp.setdefault(_fp(c), []).append(c)
        rebuilt: List[Tuple[int, Any]] = []
        used: Set[int] = set()
        for d, fp in old:
            for c in by_fp.get(fp, []):
                if id(c) not in used:
                    rebuilt.append((d, c))
                    used.add(id(c))
                    break
        found = [(depth + 1, c) for c in fresh if id(c) not in used and _fp(c) not in seen]
        seen.update(_fp(c) for _d, c in found)
        queue = queue[:i] + rebuilt + found
        print(f"│  [twin] {len(found)} new region(s) at depth {depth + 1}")
        print("└─ EDITED\n")

    (output_dir / f"twin_model_program{ext}").write_text(Path(args.source_file).read_text())
    applied = _annotate(args, dp_dir, output_dir, impact) if profile_ok else 0
    print(f"\n  SUMMARY: {asked} region(s) asked  |  {edited} edited  |  {applied} DiscoPoP "
          f"pragma(s) inserted unchecked  |  nothing was checked here — the harness judges the result")
    return 0


def main() -> int:
    from .__main__ import _load_dotenv
    _load_dotenv()
    return run(parse_args())


if __name__ == "__main__":
    sys.exit(main())
