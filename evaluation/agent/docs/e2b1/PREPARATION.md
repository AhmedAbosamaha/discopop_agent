# E2-B1 — preparation plan (27 Sep 2026; the author's decisions taken the same day, record §6)

E2-B1 is the evidence experiment on hidden facts (record §6, 26 Sep, decision 4): loops whose deciding
fact — whether the hot loop may run in parallel — is not in the loop's own statements; direction (a) a
hidden dependence, (b) a hidden independence; speed check off in every arm; primary outcome a verified
parallel program; N = 10 for (a), 5 for the rest; packaging v4; Haiku first, Qwen3-Coder-30B later (its
server setup parked). This file is the preparation plan. It was designed read-only (four studies of the
code, the screens and the record, a synthesis, and an adversarial check against the repository; 27 Sep)
and corrected by that check before it was written here. Nothing below is registered until the author
decides and the record says so.

## 1. What the agent does with a direction-(b) loop (verified in the code)

- A Tier-1 region with an applicable pattern is `DEFERRED` to Phase B (`phases/phase_a.py`, the Tier-1
  branch); the re-queue (Fix 101) fires only when EVERY DiscoPoP option fails the safety gate.
- E2-B1's agent arms run with `llm_pragmas: false` (`config/arms.json`), so Phase B applies DiscoPoP's safe
  pragma to the hot loop whatever the model does. The model is still asked — about the repetition loop,
  ranked first, whose text contains the hot loop — but in (b) its answer cannot change the hot loop's
  outcome. The twins (`twin.py`) route the same way.
- DiscoPoP alone (`discopop_capability`) is also T0.11's arm: a (b) unit is selected BECAUSE DiscoPoP alone
  parallelizes it (class A), an (a) unit because it does not (class R) — DiscoPoP alone's result is fixed
  by the selection in both directions.

So (a) can be tested as registered; (b), inside the agent and its twins, cannot show an evidence effect.

## 2. Decisions (all taken as recommended — "yes go ahead", 27 Sep; record §6. For (b): the index-permutation group starts at vas, s277 is admitted)

1. **How direction (b) is treated.**
   - A (recommended) — (b) is DESCRIPTIVE: the model alone against DiscoPoP alone (does the model alone
     parallelize a loop whose text suggests a dependence — correctly, wrongly, or not at all?); the agent
     and twin cells on (b) are a no-harm control. Recorded as a deviation from "both directions" before
     any measurement.
   - C — (b) leaves the evidence tier (showcase only); all trials go to (a).
   - B (not recommended) — an arm option that sends (b) loops to the model; needs model-written pragmas,
     an agent change (D34), a twin change, new checks; full evidence would hand the model the answer.
2. **The (a) population, by the recorded rule (one per duplicate group, the FIRST in source order).**
   - Tier 1 (the fact outside the loop's function): TSVC **s151** (the caller's argument), **s161** (the
     initial data) — both packaged; and Rodinia's group **bfs → kmeans → streamcluster** (the edge list /
     a callee's result / an index set in other functions), bfs first: it needs a deterministic synthetic
     graph input (a recorded deviation). The rule allows no exclusion for effort or for looking weak; a
     member that fails a hard constraint or a measured condition leaves with the reason, and the next in
     source order enters.
   - Tier 2 (the fact in the same function; reported apart): **s131** (its group — s131, s421, s422,
     s423: the screen links them — keeps s131) and **s424** (its own group; needs flat arrays and `xx`
     without `restrict`).
   - N = 10 for every (a) loop, tier 2 included (the record does not distinguish tiers).
3. **The (b) population, if (b) stays (option A).** Tier 1: s152 (a callee touching only index i), s171
   (`inc` set outside the function: declared in the harness header, not bound in the file), s481 (the
   initial values; its own group), s277/s258/s482 by their groups (s277 does no work with the shipped data
   — admissible? the author's call), and the index-permutation group s491 → s4113 → vas (s491 and s4113
   were T0.11 probe loops dropped from new trials on 26 Sep; re-admit, or start the group at vas).
   Predicted to fail their measured condition: s123, s482 (class R), s332 (R; and its value is a choice).
4. **The primary outcome counts only programs whose parallel construct COVERS the hot loop** (a mechanical
   check), since today "parallel" means any pragma in the program.
5. **Hypotheses and their family.** "The 18 class-R TSVC loops stay the population of every registered
   hypothesis" (26 Sep) — so E2-B1's confirmatory tests get their own names, added to the campaign's Holm
   family: (i) the evidence effect inside the agent on (a) — `full_b1_nospeed` more verified parallel
   programs than `no_evidence_b1_nospeed`; (ii) the same contrast on the twins and the interaction (the
   twins' registered purpose is H12's interaction); (iii) unsafe programs (BROKEN, racy, not compiling)
   shipped by the agent vs the model alone. With the speed check off, "correct but slower" is reported,
   not counted as unsafe.
6. **Smaller rulings (recommendations):** the H13/C2 property is waived for (b) units (a naive pragma on a
   truly independent loop passes by nature); class A is `class_table.py`'s majority of usable draws
   (fix the "FASTER in ≥ 2 of 3" wording in §6); substitution in source order when a unit fails a measured
   condition; DiscoPoP alone reported from the three v4 T0.11 draws, labelled "selected on", no test
   against it; the Qwen cells pre-registered now, run when its setup is decided; T0.15 re-run on the fixed
   DiscoPoP (B4, B9, B10) before E2-B1, as the v4 decision requires.

## 3. Measured conditions per unit (server, no model), before any trial

1. T0.1 sizes on the v4 package.
2. `prepare_tsvc.py --validate` (runs, finite, the perturbed input changes it, deterministic).
3. `naive_pragma.py` — the naive `parallel for` on the hot loop fails the gate for (a).
4. T0.11, `discopop_capability`, 3 draws on v4 with the fixed DiscoPoP: the kernel's profile names the
   deciding dependence (a) / reports Do-All with it absent (b); class R (a) / A (b).
5. `routing_check.py` on those draws: (a) the hot loop reaches the model in 3 of 3; (b) DiscoPoP's pragma
   is applied in 3 of 3.
6. A hand-read of every unit before measurement.

## 4. Build status

| item | status |
|---|---|
| `prepare_tsvc.py --suite tsvc_b1` (v4 only), s151, s161 | done, validated (27 Sep) |
| golden-render check (test_integrity 1c) | done: 35 of 35 |
| `routing_check.py` | done; checked on archived draws |
| `naive_pragma.py` | done; s151, s161 fail at TSan (Mac) |
| s131, s424 (flat + `xx`) | after decision 2 |
| Rodinia bfs packager (synthetic graph) | after decision 2 |
| (b) units (s152, s171, s481, …) | after decision 1 |
| hot-loop coverage check in the verdict | after decision 4 |
| statistics: CMH (Mantel-Haenszel OR, RBG interval), unsafe metric, direction/tier split, selectable DiscoPoP-alone arm | after decision 5 |
| registry entries for the no-model runs (T0.1, T0.11, T0.15 re-run) | before their launch |

Local check (Mac, fixed DiscoPoP): neither s151 nor s161 is Do-All; s151's hot loop (in `s151s`) is blocked
on `a`, s161's on `c` — the deciding dependence in each.
