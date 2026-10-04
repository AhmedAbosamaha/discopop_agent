#!/usr/bin/env python3
"""What a model would read for one package — the agent's request and the model alone's, side by side.

The author's rule (4 Oct 2026): every text of ours that a model reads is shown before it is used. For one
profiled package directory (the files of the package and its `.discopop`, as a run's `profiles/<suite>/<name>`
holds them) this writes, with NO model call and with each arm's own code:

    agent_system.txt, agent_request.txt            the agent's first request for its first region
    model_alone_system.txt, model_alone_request.txt   the model alone's (the mirror)
    files/                                         the files in both working copies

    venv/bin/python evaluation/agent/tools/show_requests.py <profile dir> <out dir>
        [--prompt-version 4] [--no-require-speedup] [--budget 3]
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO))
from discopop_agent import bare_llm, project as project_mod       # noqa: E402
from discopop_agent.args import gate_facts, parse_args             # noqa: E402
from discopop_agent.evidence import assemble                       # noqa: E402
from discopop_agent.llm.prompts import _system_prompt              # noqa: E402
from discopop_agent.llm.request import _build_direct_prompt        # noqa: E402
from discopop_agent.plan import build_candidates                   # noqa: E402
from discopop_agent.plan import impact as impact_mod               # noqa: E402

FIRST_REASON = "DiscoPoP found no applicable parallelism pattern for this region"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("profile", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--prompt-version", default="4")
    ap.add_argument("--no-require-speedup", action="store_true")
    a = ap.parse_args()
    work = a.profile.resolve()
    meta = json.loads((work / "meta.json").read_text())
    proj = meta.get("project") or {}
    if not proj.get("editable"):
        sys.exit("show_requests.py is for a package that names its one editable file (packaging v5)")
    units, editable = list(proj["units"]), list(proj["editable"])
    speed = [] if not a.no_require_speedup else ["--no-require-speedup"]
    project_mod.activate(project_mod.Project.discover(work, units=units, include_dirs=["."], editable=editable))
    project_mod.set_focus(str(work / editable[0]))
    saved = sys.argv
    sys.argv = ["x", "--discopop-dir", str(work / ".discopop"), "--project-dir", str(work), "--project-units",
                ",".join(units), "--project-include", ".", "--project-editable", ",".join(editable),
                "--exclude-functions", ",".join(meta.get("exclude_functions") or []), "--min-runtime-share", "0.01",
                "--prompt-version", a.prompt_version, "--check-input", "7", "--edit-mode", "direct",
                "--provider", "claude-agent-sdk", *speed]
    try:
        args = parse_args()
    finally:
        sys.argv = saved
    args.noise_floor = 0.0
    dp = work / ".discopop"
    impact = impact_mod.load_hotspots(dp, threads=os.cpu_count() or 1)
    cands = build_candidates(dp, args.source_file, args.lambda_penalty, args.min_workload, impact=impact,
                             min_impact=args.min_impact, min_runtime_share=args.min_runtime_share,
                             exclude_functions=args.exclude_functions)
    if not cands:
        sys.exit("the agent's queue is empty for this profile")
    ev = assemble(cands[0], dp / "profiler", FIRST_REASON)
    gate = gate_facts(args)
    a.out.mkdir(parents=True, exist_ok=True)
    ws = Path("/workspace") / editable[0]
    (a.out / "agent_system.txt").write_text(_system_prompt("direct", args.llm_pragmas, False, gate, args.evidence_sections))
    (a.out / "agent_request.txt").write_text(_build_direct_prompt(ev, ws, args.evidence_sections, args.llm_pragmas, gate))
    mirror = bare_llm.mirror_gate(not a.no_require_speedup, int(a.prompt_version))
    read_only = [u for u in units if u not in editable]
    (a.out / "model_alone_system.txt").write_text(bare_llm._system("mirror", mirror, one_file=True))
    (a.out / "model_alone_request.txt").write_text(bare_llm._request_mirror(editable, [], (), "", mirror, read_only))
    shutil.rmtree(a.out / "files", ignore_errors=True)
    (a.out / "files").mkdir()
    for f in sorted(work.iterdir()):
        if f.is_file() and f.suffix in (".c", ".h"):
            shutil.copy2(f, a.out / "files" / f.name)
    project_mod.activate(None)
    print(f"written to {a.out}: the agent's request is for region {cands[0].region.region_type} at line "
          f"{cands[0].region.start_line} of {Path(cands[0].source_file).name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
