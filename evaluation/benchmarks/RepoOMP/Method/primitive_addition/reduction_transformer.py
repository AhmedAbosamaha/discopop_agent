#!/usr/bin/env python3
"""Generate only scalar-addition reductions from canonical C loops.

This pass never parallelizes array-only loops. It is intentionally narrow and
requires workload verification before acceptance.
"""
import argparse
import json
import re
from pathlib import Path

FOR_RE = re.compile(r"^(\s*)(for\s*\([^)]*\))\s*\{")
ASSIGN_RE = re.compile(r"\b([A-Za-z_]\w*)\s*=\s*\1\s*\+")
CONTROL_RE = re.compile(r"\b(?:break|continue|goto|return|exit|abort)\b")


def block_end(lines, start):
    depth = 0
    for index in range(start, len(lines)):
        depth += lines[index].count("{") - lines[index].count("}")
        if index > start and depth == 0:
            return index
    return None


def transform(source, out, audit):
    lines = Path(source).read_text(errors="replace").splitlines()
    result = []
    changes = []
    index = 0
    while index < len(lines):
        line = lines[index]
        match = FOR_RE.match(line)
        if not match:
            result.append(line)
            index += 1
            continue
        end = block_end(lines, index)
        if end is None:
            result.append(line)
            index += 1
            continue
        text = "\n".join(lines[index:end + 1])
        updates = ASSIGN_RE.findall(text)
        unique = sorted(set(updates))
        if len(unique) == 1 and not CONTROL_RE.search(text) and "#pragma omp" not in text:
            variable = unique[0]
            result.append(match.group(1) + f"#pragma omp parallel for reduction(+:{variable})")
            changes.append({"line": index + 1, "variable": variable, "operator": "+"})
        result.extend(lines[index:end + 1])
        index = end + 1
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text("\n".join(result) + "\n")
    record = {"schema": "repoomp.reduction-transform.v1", "source": str(Path(source).resolve()), "output": str(Path(out).resolve()), "generated_from_rules": True, "changes": changes, "changed": bool(changes)}
    Path(audit).write_text(json.dumps(record, indent=2))
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--audit", required=True)
    args = parser.parse_args()
    print(json.dumps(transform(args.source, args.out, args.audit), indent=2))


if __name__ == "__main__":
    main()
