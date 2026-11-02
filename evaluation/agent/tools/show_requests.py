#!/usr/bin/env python3
"""What a model would read for one package — the agent's request and the model alone's, side by side.

The author's rule (4 Oct 2026): every text of ours that a model reads is shown before it is used. For one
profiled package directory (the files of the package and its `.discopop`, as a run's `profiles/<suite>/<name>`
holds them) this writes, with NO model call and with each arm's own code:

    agent_system.txt, agent_request.txt            the agent's first request for its first region
    model_alone_system.txt, model_alone_request.txt   the model alone's (the mirror)
    files/                                         the files in both working copies

    venv/bin/python evaluation/agent/tools/show_requests.py <profile dir> <out dir>
        [--prompt-version 4] [--no-require-speedup] [--llm-pragmas]
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
    ap.add_argument("--llm-pragmas", action="store_true",
                    help="the mode in which the model writes the directives (E3's llm_pragmas arms, E6)")
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
                "--provider", "claude-agent-sdk", *speed, *(["--llm-pragmas"] if a.llm_pragmas else [])]
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
    # The agent's own routing (phases/phase_a.py): a region DiscoPoP already reports with an applicable pattern
    # (Tier 1) is deferred to Phase B and never sent; the first region the model is sent is the first other one,
    # with FIRST_REASON as its reason. (A deferred region the gate then refutes can be re-queued to the model in
    # the trial itself, with another reason; that needs the gate and is not rendered here.)
    def _deferred(c: object) -> bool:
        pat = getattr(c, "pattern", None)
        return getattr(c, "tier", None) == 1 and bool(pat) and bool(pat.get("applicable_pattern"))  # type: ignore[union-attr]
    first = next((c for c in cands if not _deferred(c)), None)
    if first is None:
        sys.exit("every region of the agent's queue is deferred to DiscoPoP: the model is sent nothing at first")
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "queue.txt").write_text("".join(
        f"{n:3d}  {'deferred to DiscoPoP' if _deferred(c) else 'sent to the model'}  {c.region.region_type} "
        f"lines {c.region.start_line}-{c.region.end_line} of {Path(c.source_file).name}\n"
        for n, c in enumerate(cands, 1)))
    ev = assemble(first, dp / "profiler", FIRST_REASON)
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
        if f.is_file() and f.suffix in (".c", ".h", ".cc", ".cpp", ".hpp"):
            shutil.copy2(f, a.out / "files" / f.name)
    project_mod.activate(None)
    print(f"written to {a.out}: the agent's request is for region {first.region.region_type} at line "
          f"{first.region.start_line} of {Path(first.source_file).name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
