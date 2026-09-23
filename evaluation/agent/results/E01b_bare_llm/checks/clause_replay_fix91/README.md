# clause_replay_fix91 — every archived clause-stage rejection, judged again by the current rules (no model)

Re-run and archived on 23 Sep 2026 (commit `2b2f8a0b` + this folder): the replay behind Fix 91 had been
run on 23 Sep before and its counts quoted in the agent's `docs/FIXES.md` ("25 found, 11 reconstructible,
exactly 4 change"), but its output was never archived.

    venv/bin/python evaluation/agent/tools/clause_replay.py --out evaluation/agent/results/E01b_bare_llm/checks/clause_replay_fix91

The tool rebuilds, for every clause-stage rejection in `results/**/candidates.jsonl`, the source the gate
checked (the trial's original plus the Phase-A rewrites its log kept) and asks the CURRENT
`check_pragma_clauses` / `check_llm_pragmas` again.

| | rejections | flipped to accepted | still rejected | not reconstructible |
|---|---:|---:|---:|---:|
| E1 (`e1_r_b`, `default`) | 5 | **4 — `s281` reps 2–5** (Fix 91) | 1 | — |
| E10 (`full`, `speed_gate_*`) | 7 | 0 | 7 between them | |
| pre-campaign runs (`pilot2` 16 Sep, `local_obs1` 17 Sep, other harness checks) | 8 | 4 — `private(j)` on a counter a later loop nest re-initialises (the Fix 63 class) | 4 between them | |
| T0 instruments, suitability audit | 5 | 0 | 5 between them | |
| **total** | **25** | **8** | **3** | **14** |

**Reading.** Inside the experiments the only verdicts the current rules change are `s281` reps 2–5 — the
cases Fix 91 was written for, already replayed into E1 under v2 (`e1b_v2_verify`). The four other flips are in
runs made before the campaign's design was fixed and change no reported result. Fourteen rejections cannot be
rebuilt (no original source or log archived with them — the earliest runs, and every E10 one whose trial did
not keep its original), so for those, E10's among them, whether the current rules would accept them is not
known; it is stated as such, not assumed. `results.json`: one record per rejection with the old reason and the
new verdict.
