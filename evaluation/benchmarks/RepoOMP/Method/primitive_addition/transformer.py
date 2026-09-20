#!/usr/bin/env python3
"""Route MAP candidates into deterministic or optional STC transformation.

Deterministic mode is conservative. It never invents OpenMP clauses from weak
text evidence. High candidates with existing safe pragmas are preserved;
Middle candidates require explicit --use-llm and an STC prompt; Low stays serial.
"""
import argparse
import json
from pathlib import Path

from rule_transformer import transform as apply_rules
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from dependency_analysis.stc_builder import build_stc


def transform(source, map_json, routes_json, out, function_id=None, use_llm=False):
    graph = json.loads(Path(map_json).read_text())
    routes = json.loads(Path(routes_json).read_text())
    src = Path(source)
    selected = [r for r in routes["routes"] if function_id is None or r["function"] == function_id]
    actions = []
    high = [r for r in selected if r["confidence"] == "High"]
    middle = [r for r in selected if r["confidence"] == "Middle"]
    low = [r for r in selected if r["confidence"] == "Low"]
    code = src.read_text(errors="replace")
    if high and not middle and not low:
        audit_path = Path(str(out) + ".rules.audit.json")
        line_range = None
        if function_id is not None:
            node = next((n for n in graph["nodes"] if n.get("id") == function_id), None)
            if node is None:
                raise ValueError(f"function missing from MAP: {function_id}")
            line_range = (node["line"], node["end_line"])
        rule_audit = apply_rules(str(src), str(out), str(audit_path), line_range=line_range)
        actions.extend({"function": r["function"], "confidence": r["confidence"], "action": "rules", "blockers": r["blockers"]} for r in high)
        changed = bool(rule_audit.get("changed"))
        status = "rules_transform"
    else:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        Path(out).write_text(code)
        changed = False
        status = "identity_safe_transform"
        for r in selected:
            if r["confidence"] == "Middle" and use_llm:
                stc_path = Path(str(out) + ".stc.json")
                build_stc(str(src), map_json, routes_json, r["function"], str(stc_path))
                action = "stc_llm_pending"
            elif r["confidence"] == "Middle":
                action = "keep_serial_no_api"
            else:
                action = "keep_serial_blocker"
            actions.append({"function": r["function"], "confidence": r["confidence"], "action": action, "blockers": r["blockers"]})
    audit = {"schema": "repoomp.transform.v1", "source": str(src.resolve()), "output": str(Path(out).resolve()), "use_llm": use_llm, "changed": changed, "actions": actions, "status": status}
    Path(str(out) + ".audit.json").write_text(json.dumps(audit, indent=2))
    return audit


def main():
    ap = argparse.ArgumentParser(description="Apply conservative MAP-routed transformation")
    ap.add_argument("--source", required=True); ap.add_argument("--map", required=True); ap.add_argument("--routes", required=True); ap.add_argument("--out", required=True); ap.add_argument("--function", default=None); ap.add_argument("--use-llm", action="store_true")
    args = ap.parse_args(); result = transform(args.source, args.map, args.routes, args.out, args.function, args.use_llm); print(f"[transform] wrote {args.out} changed={result['changed']} actions={len(result['actions'])}")

if __name__ == "__main__": main()
