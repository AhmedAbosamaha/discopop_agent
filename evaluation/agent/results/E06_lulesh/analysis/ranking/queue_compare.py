"""E6: the queue the agent built (ranked by measured time saved) beside the queue the
same profile gives without the measurement (`--no-hotspots`: DiscoPoP's workload proxy).

No model, no profiling: `build_candidates` is called on a run's initial profile exactly as
`run.py` calls it under `--no-hotspots` (an ImpactModel with no measurements), with the
trial's own --min-workload, λ, --min-runtime-share, --exclude-functions and editable file.
The measured queue is the "Initial candidates" table the trial printed in its agent.log.

    python queue_compare.py --profile DIR --trial TRIAL_DIR [--trial ...] > out.md

DIR holds `.discopop` (FileMapping.txt, profiler/Data.xml, profiler/dynamic_dependencies.txt,
profiler/loop_counter_output.txt, explorer/patterns.json) and the program's sources; a
FileMapping written on another machine is read with its paths moved into DIR by file name.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[6]))
from discopop_agent import project as project_mod  # noqa: E402
from discopop_agent.plan import build_candidates  # noqa: E402
from discopop_agent.plan.impact import ImpactModel  # noqa: E402

INPUTS = ("FileMapping.txt", "profiler/Data.xml", "profiler/dynamic_dependencies.txt",
          "profiler/loop_counter_output.txt", "explorer/patterns.json")


def flags(trial: Path) -> Dict[str, str]:
    cmd = json.loads((trial / "trial.json").read_text())["agent_cmd"]
    cmd = cmd if isinstance(cmd, list) else cmd.split()
    out: Dict[str, str] = {}
    for i, a in enumerate(cmd):
        if a.startswith("--"):
            k, _, v = a.partition("=")
            out[k] = v or (cmd[i + 1] if i + 1 < len(cmd) and not cmd[i + 1].startswith("--") else "")
    return out


def measured_queue(log: Path) -> List[Tuple[str, str, str, str]]:
    """(region id, type, % run, name) in the order the trial printed them."""
    L = log.read_text(errors="replace").split("\n")
    i = next(k for k, l in enumerate(L) if l.strip() == "Initial candidates")
    rows = []
    for l in L[i + 3:]:
        if not l.strip():
            break
        m = re.match(r"\s*(\d+:\d+)\s+(\w+)\s+[\d.]+ ms\s+([\d.]+)%\s+\w+\s+\d\s+\d\s+(.*)$", l)
        if m:
            rows.append((m.group(1), m.group(2), m.group(3), m.group(4).strip()))
    return rows


def label(trial: Path) -> str:
    """`run/repN` from .../runs/<run>/benchmarks/<suite>/<kernel>/<arm>/<model>/repN"""
    return f"{trial.parents[5].name}/{trial.name}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", required=True, type=Path)
    ap.add_argument("--trial", action="append", required=True, type=Path)
    ap.add_argument("--source", default="", help="where the profile's files were copied from (for the header)")
    a = ap.parse_args()
    f = flags(a.trial[0])
    editable = f.get("--project-editable", "")
    source = editable.split(",")[0]
    with tempfile.TemporaryDirectory() as tmp:
        # the profile is only read: the moved FileMapping is written into a copy of .discopop
        root = Path(tmp) / "p"
        shutil.copytree(a.profile, root, ignore=shutil.ignore_patterns(".discopop"))
        dd = root / ".discopop"
        for rel in INPUTS:
            (dd / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(a.profile / ".discopop" / rel, dd / rel)
        fm = [l.split("\t") for l in (dd / "FileMapping.txt").read_text().splitlines() if "\t" in l]
        (dd / "FileMapping.txt").write_text(
            "".join(f"{i}\t{root / Path(p.strip()).name}\n" for i, p in fm))
        project_mod.activate(project_mod.Project.discover(root, editable=[source]))
        proxy = build_candidates(
            dd, str(root / source), float(f.get("--lambda-penalty", "1.0") or 1.0),
            float(f.get("--min-workload", "0.0") or 0.0), impact=ImpactModel(threads=1),
            min_runtime_share=float(f.get("--min-runtime-share", "0") or 0),
            exclude_functions=tuple(x for x in f.get("--exclude-functions", "").split(",") if x))
    print(f"# Queue without the measurement vs the agent's queue — `{a.source or a.profile}`\n")
    print("Inputs (sha256): " + ", ".join(
        f"`{rel}` {hashlib.sha256((a.profile / '.discopop' / rel).read_bytes()).hexdigest()[:12]}"
        for rel in INPUTS) + "\n")
    print(f"Flags taken from `{a.trial[0]}/trial.json`: editable `{source}`, --min-runtime-share "
          f"{f.get('--min-runtime-share', '0')} (inert without the measurement), "
          f"{len([x for x in f.get('--exclude-functions', '').split(',') if x])} excluded functions.\n")
    meas = {str(t): measured_queue(t / "agent.log") for t in a.trial}
    pos = {k: {r[0]: (n + 1, r[2]) for n, r in enumerate(v)} for k, v in meas.items()}
    print(f"Proxy queue: {len(proxy)} regions.  " + "  ".join(
        f"Measured queue of `{label(Path(k))}`: {len(v)} regions." for k, v in meas.items()) + "\n")
    hdr = " | ".join(f"measured # ({label(Path(k))})" for k in meas)
    print(f"| proxy # | region | type | lines | tier | pattern | W | proxy score | % run | {hdr} |")
    print("|" + "---|" * (9 + len(meas)))
    for n, c in enumerate(proxy, 1):
        r = c.region
        share = next((p[r.region_id][1] for p in pos.values() if r.region_id in p), "")
        cells = " | ".join(str(p[r.region_id][0]) if r.region_id in p else "—" for p in pos.values())
        name = r.name if r.region_type == "function" else ""
        print(f"| {n} | {r.region_id} {name} | {r.region_type} | {r.start_line}–{r.end_line} | {c.tier} | "
              f"{c.pattern_type or ''} | {int(c.workload_estimate)} | {c.score:.2f} | {share} | {cells} |")


if __name__ == "__main__":
    main()
