#!/usr/bin/env python3
"""Every clause-stage rejection ever archived, judged again by the CURRENT clause rules — no model.

The gate's clause stage is static (no build, no run), so a change to it can be replayed exactly:
rebuild the source each archived candidate was checked against — the trial's original plus the
Phase-A rewrites the log kept before it (`marginal_replay`'s rule) — and ask the current
`check_pragma_clauses` (a DiscoPoP pragma, Phase B) or `check_llm_pragmas` (a model's pragma,
Phase A) again. A verdict that flips is listed with both reasons, so each can be read.

    venv/bin/python evaluation/agent/tools/clause_replay.py --out evaluation/agent/analysis/clause_replay
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO))
import campaign  # noqa: E402
from marginal_replay import _apply  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_include  # noqa: E402
harness_include.install()   # every build finds prepared/_harness (D39)


def _kept_flags(log: str) -> List[bool]:
    """Kept (True) / reverted (False) for each Phase-A candidate that passed, in order."""
    out: List[bool] = []
    for line in log.split("PHASE B")[0].splitlines():
        if "Quality gate PASSED" in line:
            out.append(True)
        elif "reverting" in line and out:
            out[-1] = False
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    from discopop_agent.pragmas import check_llm_pragmas, check_pragma_clauses

    a.out.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, Any]] = []
    for cj in sorted(campaign.RESULTS.glob("**/agent_patches/candidates.jsonl")):
        d = cj.parent.parent
        cands = [json.loads(l) for l in cj.read_text().splitlines() if l.strip()]
        if not any(c.get("stage") == "clause" for c in cands):
            continue
        t = json.loads((d / "trial.json").read_text()) if (d / "trial.json").exists() else {}
        name = str(t.get("source") or "")
        originals = sorted(d.glob("original.*"))
        base: Dict[str, Any] = {"trial": str(d.relative_to(campaign.RESULTS)), "benchmark": t.get("benchmark"),
                                "arm": t.get("arm")}
        if not name or not originals or not (d / "agent.log").exists():
            rows.append({**base, "verdict": "not reconstructible (no original / source name / log)"})
            continue
        kept = _kept_flags((d / "agent.log").read_text())
        state = originals[0].read_text()
        n_passed_a = 0
        for c in cands:
            patch = d / "agent_patches" / str(c.get("patch"))
            if c.get("stage") == "clause" and patch.exists():
                rec = {**base, "phase": c["phase"], "region": c.get("region_id"),
                       "old": (c.get("diagnostic") or "")[:300]}
                with tempfile.TemporaryDirectory(prefix="clause_replay_") as tmp:
                    f = Path(tmp) / name
                    f.write_text(state)
                    diff = patch.read_text()
                    try:
                        new = (check_pragma_clauses(diff, str(f)) if c["phase"] == "B"
                               else check_llm_pragmas(diff, str(f)))
                        rec["new"] = new
                        rec["verdict"] = "still rejected" if new else "FLIPPED to accepted"
                    except Exception as e:           # noqa: BLE001 - reported per candidate
                        rec["verdict"] = f"replay failed: {type(e).__name__}: {e}"
                rows.append(rec)
            if c.get("phase") == "A" and c.get("passed"):
                if n_passed_a < len(kept) and kept[n_passed_a] and patch.exists():
                    try:
                        state = _apply(state, patch, name)
                    except RuntimeError as e:
                        rows.append({**base, "verdict": f"state not rebuilt: {e}"[:300]})
                        break
                n_passed_a += 1
    (a.out / "results.json").write_text(json.dumps(rows, indent=1, default=str) + "\n")
    judged = [r for r in rows if r.get("verdict") in ("still rejected", "FLIPPED to accepted")]
    flipped = [r for r in judged if r["verdict"] == "FLIPPED to accepted"]
    head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    print(f"{len(rows)} archived clause rejection(s), {len(judged)} re-judged, {len(flipped)} flipped "
          f"(agent tree at {head.stdout.strip()}, uncommitted changes included)")
    for r in rows:
        print(f"- {r.get('benchmark')} [{r.get('arm')}] phase {r.get('phase', '?')} {r.get('region', '')}: "
              f"{r['verdict']}" + (f"\n    was: {r['old'][:150]}" if r.get('verdict') == 'FLIPPED to accepted' else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
