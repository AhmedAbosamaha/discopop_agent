# `agent/prepared/` — the generated benchmark packages (NOT in git)

What is here: every benchmark as the harness hands it to a trial, one folder per `<suite>/<kernel>`
with its source(s), `meta.json` (provenance, sizes, functions the agent may not edit) and the
packaging's own harness code. Generated from the sources in `evaluation/benchmarks/` — nothing
here is edited by hand.

Regenerate: `agent/benchmark prepare` (PolyBench), `agent/tools/prepare_tsvc.py`,
`agent/tools/prepare_apps.py [--validate] [--references]` (md, is, hotspot, LULESH, …),
`agent/tools/prepare_calib.py`, and E2-B1's `agent/tools/prepare_tsvc.py --suite tsvc_b1 --layout v4
--out agent/prepared/tsvc_b1` and `agent/tools/prepare_bfs.py --out agent/prepared/rodinia_b1` (their
measurement headers go to `_harness/`), and the clean layout's `agent/tools/prepare_tsvc.py --suite tsvc_c1
--layout v5 --out agent/prepared/tsvc_c1 --validate` (packaging v5, 4 Oct 2026: `<name>.c` holds the loop's
function and one include, nothing else — the ONE file a model's changes are taken from; `data.h` the
declarations; `main.c` our `main`, repetition loop and `pb_mix`; the measurement header under `_harness/`; its
references go to `agent/reference_solutions/tsvc_c1/`). Every package records a digest, and every trial checks the
package before and after it ran (`package_integrity`). The server generates its own; a sync
does NOT regenerate them — regenerate after changing a packager.
