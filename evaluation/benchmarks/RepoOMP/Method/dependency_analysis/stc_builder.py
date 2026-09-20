#!/usr/bin/env python3
"""Serialize five-field Structured Transformation Context (STC)."""
import argparse
import json
import re
from pathlib import Path


def _function_block(text, name):
    pat = re.compile(r"(?:static\s+)?(?:\w[\w\s*]+)\b" + re.escape(name) + r"\s*\([^;{}]*\)\s*\{")
    m = pat.search(text)
    if not m:
        return ""
    depth = 0
    for i in range(m.end() - 1, len(text)):
        if text[i] == "{": depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0: return text[m.start():i + 1]
    return text[m.start():]


def build_stc(source, map_json, route_json, function_id, out):
    graph = json.loads(Path(map_json).read_text())
    routing = json.loads(Path(route_json).read_text())
    node = next(n for n in graph["nodes"] if n.get("id") == function_id)
    route = next(r for r in routing["routes"] if r["function"] == function_id)
    src_path = Path(graph["root"]) / node["file"]
    text = Path(source or src_path).read_text(errors="replace")
    visible = {x["path"]: x["global_definitions"] for x in graph["files"] if x["path"] == node["file"]}
    calls = [n for n in graph["nodes"] if n.get("kind") == "function" and n.get("name") in node.get("calls", [])]
    stc = {
        "schema": "repoomp.stc.v1",
        "candidate": {"function": function_id, "name": node["name"], "file": node["file"], "line": node["line"]},
        "target_source_range": _function_block(text, node["name"]),
        "visible_shared_state_definitions": visible,
        "required_symbol_definitions": {"functions": calls, "file": node["file"]},
        "transitive_call_summaries": [{"id": c["id"], "name": c["name"], "file": c["file"], "line": c["line"], "global_reads": c.get("global_reads", []), "global_writes": c.get("global_writes", []), "blockers": c.get("blockers", [])} for c in calls],
        "blocker_constraints": {"confidence": route["confidence"], "blockers": route["blockers"], "must_preserve_serial": route["confidence"] == "Low", "allowed_change_scope": node["file"]},
        "prompt_policy": "Only change target range. Use supplied evidence. Preserve buildability and workload checks. Do not add unsynchronized shared writes. Do not modify outside target range.",
    }
    Path(out).parent.mkdir(parents=True, exist_ok=True); Path(out).write_text(json.dumps(stc, indent=2))
    return stc


def main():
    ap = argparse.ArgumentParser(description="Build five-field RepoOMP STC")
    ap.add_argument("--source", default=None); ap.add_argument("--map", required=True, dest="map_json"); ap.add_argument("--routes", required=True, dest="route_json"); ap.add_argument("--function", required=True, dest="function_id"); ap.add_argument("--out", required=True)
    args = ap.parse_args(); stc = build_stc(args.source, args.map_json, args.route_json, args.function_id, args.out)
    print(f"[stc] wrote {args.out} candidate={stc['candidate']['name']}")

if __name__ == "__main__": main()
