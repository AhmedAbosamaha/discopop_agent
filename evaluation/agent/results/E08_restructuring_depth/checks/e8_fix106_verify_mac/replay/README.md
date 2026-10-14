# Fix 106 checked without a model (14 Oct 2026, Mac)

Run from the repository root with the repository's venv.

- `scripts/settle_archive.py evaluation/agent/results` → `settle_archive.txt`: every archived trial in which
  Settle dropped an orphan rewrite and something then failed to apply; for each orphan, whether a later
  accepted rewrite changed a region it exposed (`reshaped`) or does not apply without it (`needs`).
  Last line: 24 trials, 15 with a later rewrite built on the orphan, 9 without (E2-B1's `bfs`).
- `scripts/bfs_shift_check.py <bfs full_b1_nospeed rep5>` → `bfs_shift_check.txt`: Phase B takes the
  pragma's region fingerprint after an earlier pragma shifted the lines (candidate Fix 107).
- `scripts/smoke_replay.py TRIAL OUT`: the trial's change log rebuilt from the archive and replayed
  through the agent's `_settle` (gate stood in). `before/`: Settle as it stood (`2dbe2c0b3`) — the notes
  equal the archived ones for both smoke trials (positive control). `after/`: the repaired Settle —
  both smoke trials keep all six changes; E1-v6 `s331` rep 2 and E2-B1 `bfs` `no_evidence` rep 3 keep
  their chains; E2-B1 `bfs` `full_b1_nospeed` rep 5 (no chain) prints the archived notes unchanged.
- `benchmarks/tsvc_c5/s2251/fix106_replay_depth{1,2}/`: the harness's `verify-source` on the two
  finished files against the original (LARGE, 2 and 4 threads, 3 repeats): both exact (also seeded),
  4 and 3 pragmas; Mac timings are no evidence of speed.
