#!/usr/bin/env python3
"""Deterministic confidence routing over a RepoOMP MAP graph."""
import argparse
import json
from pathlib import Path


def route_node(node):
    blockers = set(node.get("blockers", []))
    if blockers:
        return "Low"
    if node.get("loop_count", 0) and (node.get("reduction") or node.get("openmp")):
        return "High"
    if node.get("loop_count", 0):
        return "Middle"
    return "Low"


def route_map(map_path, out_path):
    graph = json.loads(Path(map_path).read_text())
    routes = []
    for node in graph.get("nodes", []):
        if node.get("kind") != "function":
            continue
        label = route_node(node)
        routes.append({
            "function": node["id"],
            "name": node.get("name"),
            "file": node.get("file"),
            "line": node.get("line"),
            "confidence": label,
            "blockers": node.get("blockers", []),
            "reasons": {
                "loop_count": node.get("loop_count", 0),
                "reduction": bool(node.get("reduction")),
                "global_reads": node.get("global_reads", []),
                "global_writes": node.get("global_writes", []),
                "io_calls": node.get("io_calls", []),
                "serial_calls": node.get("serial_calls", []),
                "indirect_memory": bool(node.get("indirect_memory")),
                "external_calls": node.get("external_calls", []),
            },
            "action": {"High": "rules", "Middle": "stc_llm", "Low": "keep_serial"}[label],
        })
    result = {
        "schema": "repoomp.routing.v1",
        "map": str(Path(map_path).resolve()),
        "rules": {
            "High": "loop or reduction evidence and no propagated blocker",
            "Middle": "loop evidence without blocker but incomplete direct rule evidence",
            "Low": "any propagated shared-state, IO, serial, indirect, or external blocker",
        },
        "routes": routes,
        "counts": {x: sum(r["confidence"] == x for r in routes) for x in ("High", "Middle", "Low")},
    }
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(result, indent=2))
    return result


def main():
    ap = argparse.ArgumentParser(description="Route MAP functions by deterministic confidence rules")
    ap.add_argument("--map", required=True, dest="map_path")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    result = route_map(args.map_path, args.out)
    print(f"[route] wrote {args.out} routes={len(result['routes'])} counts={result['counts']}")


if __name__ == "__main__":
    main()
