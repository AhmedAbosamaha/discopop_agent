#!/usr/bin/env python3
"""Auditable reference-guided function replacement.

Reference source is explicit upper-bound material, never implicit method output.
Only named function body is replaced. Full candidate still requires verifier.
"""
import argparse
import json
import re
from pathlib import Path


def function_span(text, name):
    pat = re.compile(r"(?:static\s+)?(?:[A-Za-z_]\w*[\s*]+)+" + re.escape(name) + r"\s*\([^;{}]*\)\s*\{")
    m = pat.search(text)
    if not m:
        raise ValueError(f"function not found: {name}")
    depth = 0
    for pos in range(m.end() - 1, len(text)):
        if text[pos] == "{": depth += 1
        elif text[pos] == "}":
            depth -= 1
            if depth == 0:
                return m.start(), pos + 1, text[m.start():pos + 1]
    raise ValueError(f"unbalanced function: {name}")


def replace_function(source, reference, name, out, audit):
    base = Path(source).read_text(errors="replace")
    ref = Path(reference).read_text(errors="replace")
    start, end, old = function_span(base, name)
    _, _, new = function_span(ref, name)
    result = base[:start] + new + base[end:]
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(result)
    Path(audit).parent.mkdir(parents=True, exist_ok=True)
    record = {"schema": "repoomp.reference-guided.v1", "source": str(Path(source).resolve()),
              "reference": str(Path(reference).resolve()), "output": str(Path(out).resolve()),
              "function": name, "changed": old != new,
              "scope": "single-function", "reference_is_upper_bound": True,
              "accepted": False, "reason": "requires workload and performance verification"}
    Path(audit).write_text(json.dumps(record, indent=2))
    return record


def main():
    ap = argparse.ArgumentParser(description="Replace one function from explicit reference source")
    ap.add_argument("--source", required=True); ap.add_argument("--reference", required=True)
    ap.add_argument("--function", required=True); ap.add_argument("--out", required=True); ap.add_argument("--audit", required=True)
    args = ap.parse_args(); r = replace_function(args.source, args.reference, args.function, args.out, args.audit)
    print(json.dumps(r, indent=2))


if __name__ == "__main__":
    main()
