# `agent/prepared/` — the generated benchmark packages (NOT in git)

What is here: every benchmark as the harness hands it to a trial, one folder per `<suite>/<kernel>`
with its source(s), `meta.json` (provenance, sizes, functions the agent may not edit) and the
packaging's own harness code. Generated from the sources in `evaluation/benchmarks/` — nothing
here is edited by hand.

Regenerate: `agent/benchmark prepare` (PolyBench), `agent/tools/prepare_tsvc.py`,
`agent/tools/prepare_apps.py [--validate] [--references]` (md, is, hotspot, LULESH, …),
`agent/tools/prepare_calib.py`, and E2-B1's `agent/tools/prepare_tsvc.py --suite tsvc_b1 --layout v4
--out agent/prepared/tsvc_b1` and `agent/tools/prepare_bfs.py --out agent/prepared/rodinia_b1` (their
measurement headers go to `_harness/`). Every package records a digest, and every trial checks the
package before and after it ran (`package_integrity`). The server generates its own; a sync
does NOT regenerate them — regenerate after changing a packager.
