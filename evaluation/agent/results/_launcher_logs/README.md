# Launcher logs — provenance for the runs executed on the server

One log per launch (`YYYYMMDD_HHMMSS.log`): the exact `agent/benchmark run` command line, the
per-trial progress, and the credential sweep that closes every job. The run records themselves
are in the sibling `results/<run_id>/` directories; these logs are what ties a run to the
command, the host and the moment it was launched, which a run's own manifest does not preserve.

Copied from the old harness checkout (`~/new_benchmark_harness/agent/runs/_launcher/`) on
2026-09-20, when the harness moved into this repository — the logs of runs launched before the
move would otherwise have been lost with it. Later launches write to
`evaluation/agent/runs/_launcher/` on the server and are fetched the same way.
