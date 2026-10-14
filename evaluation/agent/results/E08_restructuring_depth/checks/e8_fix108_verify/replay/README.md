# Fix 108 checked without a model (14 Oct 2026)

Run from the repository root with the repository's venv.

- `scripts/crash_census.py` → `crash_census.txt`: in the counted depth-0 trials of E3 (90 `default_v5`, 90
  `llm_pragmas_v5`) and E3b (35 `default_v5`), every trial whose model was sent D40's message that its program
  crashed at the timing size — read in `requests.jsonl` (the agent.log's feedback panel is cut at 30 lines and
  loses the diagnostic) — and how many rewrites the trial had kept before its last `pattern_broken` verdict
  (0 everywhere: the program before each rewrite was the original, so each crash was the rewrite's own).
- `../features_before.txt` and `../features_after.txt`: the feature check `size-crash-depth` on the agent as it
  stood (`4074ea185`: its four changed files put back, the check kept) and on the repaired agent, both on the Mac.
  `../features_all.txt`: every feature check on the repaired agent.
- `scripts/depth1_case_log.py` → `depth1_case_as_it_stood.txt`, `depth1_case_repaired.txt`: the check's depth-1 case
  (a 20-line program; the stand-in model first writes a stack array of the loop's length, then its heap version;
  `--timing-cflags=-DDP_BIG`) with the lines of its log that carry the verdicts, and the diagnostic each later
  request carried. As it stood: the stack version kept `safe_deferred`; at depth 1 the heap version turned back
  twice with "the program with DiscoPoP's pragmas CRASHED at the timing size" — the program before it was the one
  that crashed — and Phase B drops both pragmas as unsafe at size: the second smoke in miniature. Repaired: the
  stack version sent back at depth 0 (`D40 size run: CRASHED`), the heap version kept after its size run.
- `scripts/size_replay.py TRIAL OUT [--timing-flag F]`: the second smoke's depth-2 trial
  (`preflight/e8v5_smoke2/…/depth2_v5/…/rep1`) through D40 as it stood and as repaired, with the agent's own
  `judge_as_shipped`, its staging and the real build and run (the safety gate stood in by the trial's recorded
  verdicts). Case A: the depth-0 rewrite (`0000`, `s_vals[LEN_1D + 1]` on the stack), a deeper level to come;
  case B: the depth-1 rewrite on it (`0004`, adds `b_snapshot[LEN_1D]`); case C: the model's second depth-2
  attempt (`0013`, `s_vals` on the heap) at the last level, timed against the two kept rewrites, then both
  programs alone at the timing size. `size_replay_mac_standard.json`: on the Mac at `-DSTANDARD_DATASET`
  (`LEN_1D` 4,000,000; the trial's own size needs more memory than the Mac's rule allows).
  `size_replay_server_large.json`: on the server at the trial's own `-DLARGE_DATASET` (`LEN_1D` 32,000,000),
  run over ssh from the synced commit, no model, no credential.
- `scripts/smoke3_check.py RUN_DIR`: the third smoke's criterion as pre-registered (§6, 14 Oct, "E8's third smoke
  pre-registered"), committed before the smoke ran; on the second smoke's archive it holds (positive control).
- `scripts/depth1_case_log.py` runs with the repository on the path: `PYTHONPATH=. venv/bin/python …`.
