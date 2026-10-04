#!/usr/bin/env python3
"""Print the request the agent would send for the first candidate of a profiled work directory (no model call).

    python v5_prompt.py <work dir> <name> v4|v5
"""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[7]
sys.path.insert(0, str(REPO))
from discopop_agent import project as project_mod                 # noqa: E402
from discopop_agent.args import parse_args                         # noqa: E402
from discopop_agent.evidence import assemble                       # noqa: E402
from discopop_agent.llm.prompts import PROMPT_VERSIONS             # noqa: E402
from discopop_agent.llm.request import _build_direct_prompt        # noqa: E402
from discopop_agent.plan import build_candidates                   # noqa: E402
from discopop_agent.plan import impact as impact_mod               # noqa: E402
from discopop_agent.types import GateFacts                         # noqa: E402

work, name, layout = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3]
dp = work / ".discopop"
if layout == "v5":
    proj = project_mod.Project.discover(work, units=[f"{name}.c", "main.c"], include_dirs=["."])
    project_mod.activate(proj)
    project_mod.set_focus(str(work / f"{name}.c"))
    argv = ["--project-dir", str(work), "--project-units", f"{name}.c,main.c", "--project-include", "."]
else:
    argv = ["--source-file", str(work / f"{name}.c")]
sys.argv = ["x", "--discopop-dir", str(dp), *argv, "--exclude-functions", "main,pb_mix",
            "--min-runtime-share", "0.01", "--prompt-version", "3"]
args = parse_args()
impact = impact_mod.load_hotspots(dp, threads=os.cpu_count() or 1)
cands = build_candidates(dp, args.source_file, args.lambda_penalty, args.min_workload, impact=impact,
                         min_impact=args.min_impact, min_runtime_share=args.min_runtime_share,
                         exclude_functions=args.exclude_functions)
c = cands[0]
ev = assemble(c, dp / "profiler", "")
gate = GateFacts(require_speedup=False, n_inputs=2, changes=tuple(PROMPT_VERSIONS[3]))
print(_build_direct_prompt(ev, Path("/ws") / Path(c.source_file).name, None, False, gate))
