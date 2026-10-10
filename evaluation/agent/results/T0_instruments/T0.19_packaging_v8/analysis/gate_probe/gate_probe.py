#!/usr/bin/env python3
"""T0.19, a no-model probe of the agent's own gate (read-only; run on the server from the repository root):
what does the gate's dependence stage say to the plainest right answer on each loop expected under test — the
loop as it stands with one directive above it?

The stage reads DiscoPoP's record of what blocks a Do-All on the loop (explorer/doall_prevented.json) and fails
a directive when a blocker was OBSERVED. A reduction clause resolves exactly such a dependence; this asks, on
the profiles of the class draw, whether the stage tells the two apart.

    venv/bin/python <this file> RUN_DIR        (e.g. evaluation/agent/runs/t0_11_c4_a)
"""
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT))
from discopop_agent.gate.dependences import annotated_loop_lines, dependence_evidence  # noqa: E402

RUN = Path(sys.argv[1])
PREP = ROOT / "evaluation" / "agent" / "prepared" / "tsvc_c4"
CASES = {
    # loop: the directive a model would put above the loop as it stands
    "s314": "#pragma omp parallel for reduction(max:x)",
    "s316": "#pragma omp parallel for reduction(min:x)",
    "s3113": "#pragma omp parallel for reduction(max:max)",
    "s311": "#pragma omp parallel for reduction(+:sum)",        # the control: an operator DiscoPoP writes itself
    "s3111": "#pragma omp parallel for reduction(+:sum)",
    "s319": "#pragma omp parallel for reduction(+:sum)",
}
for name, pragma in CASES.items():
    src = (PREP / name / f"{name}.c").read_text()
    lines = src.splitlines()
    at = next(i for i, l in enumerate(lines) if re.match(r"\s*for \(int i\b", l))
    indent = re.match(r"\s*", lines[at]).group(0)
    new = lines[:at] + [indent + pragma] + lines[at:]
    diff = "".join(difflib.unified_diff([l + "\n" for l in lines], [l + "\n" for l in new], f"a/{name}.c", f"b/{name}.c"))
    dp = RUN / "profiles" / "tsvc_c4" / name / ".discopop"
    if not dp.exists():
        print(f"{name}: no profile at {dp}")
        continue
    fid = None
    fm = dp / "FileMapping.txt"
    for row in fm.read_text().splitlines():
        parts = row.split("\t")
        if len(parts) >= 2 and parts[1].endswith(f"/{name}.c"):
            fid = int(parts[0])
    loop_lines = annotated_loop_lines(diff)
    # the region the agent would name: the loop under study — from its `for` line to its closing brace
    depth, end = 0, at
    for j in range(at, len(lines)):
        depth += lines[j].count("{") - lines[j].count("}")
        if depth == 0 and j > at:
            end = j
            break
    ev = dependence_evidence(str(dp), fid, at + 1, end + 1, loop_lines=loop_lines)
    prevented = []
    try:
        for r in json.loads((dp / "explorer" / "doall_prevented.json").read_text()):
            if r.get("loop_file") == fid:
                prevented.append({k: r.get(k) for k in ("loop_start", "loop_end", "origin", "type", "var", "var_name", "dep_type") if k in r})
    except (OSError, ValueError) as e:
        prevented = [f"unreadable: {e}"]
    print(f"== {name}: `{pragma}` above the loop at line {at + 1} (file id {fid}; loop lines read from the patch: {loop_lines})")
    print(f"   the stage's verdict: {ev.verdict}" + ("   -> the gate REFUSES this directive" if ev.contradicts else "   -> not refused by this stage"))
    print(f"   {ev.diagnostic[:330]}")
    print(f"   DiscoPoP's blockers recorded for this file: {prevented[:6]}")
print("GATE_PROBE_DONE")
