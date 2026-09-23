# `agent/runs/` — working copies of runs (NOT in git)

What is here: every run as `agent/benchmark run` wrote it (on the server) or `agent/tools/server.sh
fetch` copied it back (on the Mac) — the same files as the archive in `agent/results/`, PLUS the
DiscoPoP profile trees (`profiles/**/.discopop/`, several MB to GB per benchmark), the trials'
scratch copies (`work/`) and binaries. `_launcher/` holds the server's launcher logs.

**Where the results are:** `agent/results/<EXPERIMENT>/runs/<run_id>/` — tracked, complete except
for the three things above. `agent/tools/campaign.py check` fails if a run here was never archived.

**Safe to delete on the Mac** once a run is archived: the server keeps its own copy, and the
profile trees are regenerable. Needed only to resume a run, re-archive it, or inspect a profile.
Do not touch the server's copy while a run is in progress.
