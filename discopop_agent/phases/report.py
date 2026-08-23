"""
What the run prints and what it writes down
---------------------------------------------
The banner states the configuration a run actually used — worth having in the
log, since several defaults are computed from other flags rather than fixed.
The candidate table has two shapes: ranked by measured time saved when hotspot
detection has run, and by the workload proxy when it has not.

`accepted.json` is rewritten at the end to describe the FILE, not everything
that was ever provisionally accepted; a record of work that was later reverted
is worse than no record.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from ..args import AgentArguments
from ..gate import find_archer


_REGION_LABEL = {"loop": "loop", "function": "function", "cu": "block"}
def _write_record(output_dir: Path, record: dict, dry_run: bool = False) -> None:
    """Append one accepted region to accepted.json.

    A dry run still evaluates Tier-1 patches for real (it only skips the LLM),
    so its verdicts belong in the printed summary — but --dry-run promises no
    file changes, so nothing is written."""
    if dry_run:
        return
    f = output_dir / "accepted.json"
    records: List[dict] = json.loads(f.read_text()) if f.exists() else []
    records.append(record)
    f.write_text(json.dumps(records, indent=2))
def _print_candidates(candidates: list) -> None:
    """Print candidate table. candidates is a list of (depth, HotspotCandidate)."""
    measured = any(c.impact_seconds is not None for _d, c in candidates)
    if measured:
        # Ranked by time saved: show the numbers the ranking is actually made of.
        print(f"{'Region ID':<12} {'Type':<10} {'Saves':>9}  {'% run':>7}  {'Hot':>5}  "
              f"{'Tier':>4}  {'Depth':>5}  Name")
        print("-" * 86)
        for depth, c in candidates:
            r = c.region
            name = r.name or f"lines {r.start_line}–{r.end_line}"
            saves = f"{c.impact_seconds*1e3:.1f} ms" if c.impact_seconds is not None else "—"
            frac = f"{c.runtime_fraction*100:.1f}%" if c.runtime_fraction is not None else "—"
            print(f"  {r.region_id:<10} {r.region_type:<10} {saves:>9}  {frac:>7}  "
                  f"{(c.hotness or '—'):>5}  {c.tier:>4}  {depth:>5}  {name}")
    else:
        print(f"{'Region ID':<12} {'Type':<10} {'Score':>7}  {'Tier':>4}  {'Depth':>5}  {'Workload':>12}  Name")
        print("-" * 76)
        for depth, c in candidates:
            r = c.region
            name = r.name or f"lines {r.start_line}–{r.end_line}"
            print(f"  {r.region_id:<10} {r.region_type:<10} {c.score:>7.1f}  {c.tier:>4}  {depth:>5}  {c.workload_estimate:>12,.0f}  {name}")
    print()
def _print_banner(args: AgentArguments) -> None:
    print(f"\n{'='*60}")
    print("  DiscoPoP Agentic Controller")
    print(f"{'='*60}")
    print(f"  Source         : {args.source_file}")
    print(f"  DiscoPoP dir   : {args.discopop_dir}")
    print(f"  Model          : {args.model}")
    print(f"  Budget         : {args.budget} LLM retries/region "
          f"(+{args.build_retries} free build fixes)")
    print(f"  λ penalty      : {args.lambda_penalty}")
    print(f"  Min workload   : {args.min_workload}")
    print(f"  Restruct. depth: {args.restructure_depth} "
          f"(Tier-2 allowed at depth 0–{args.restructure_depth})")
    print(f"  Quality gate   : Tier-1 = all but speed, no escalation; "
          f"Tier-2 = full")
    _archer = find_archer()
    print(f"  TSan           : "
          + (f"barrier-aware (archer: {_archer})" if _archer else
             "no libarcher — TSan cannot see OpenMP barriers and will report "
             "any two parallel regions as racing; falling back to the "
             "barrier heuristic. Build one: discopop_agent/tools/build_archer.sh"))
    print(f"  Speedup gate   : "
          + (f"require ≥ {args.min_measured_speedup}× measured"
             if args.require_speedup else "OFF (--no-require-speedup)"))
    print(f"  Dry run        : {args.dry_run}")
    if args.provider == "openai-compat":
        llm_mode = f"{args.model} @ {args.api_base} (openai-compat)"
    else:
        llm_mode = args.model
    print(f"  LLM mode       : {llm_mode}")
    print(f"  Edit mode      : {args.edit_mode}")
    print(f"  Re-profiling   : "
          + ("fast refresh (compile only) between rewrites; full before a deeper "
             "level and before Phase B" if args.fast_refresh
             else "full (instrument + run + explore) after every kept rewrite")
          + ("; LLM judges static deps in new code" if args.llm_deps else ""))
    print(f"  Pragmas        : "
          + ("LLM writes them with the rewrite, gate decides (--llm-pragmas)"
             if args.llm_pragmas else "DiscoPoP writes them in Phase B"))
    print(f"{'='*60}\n")
