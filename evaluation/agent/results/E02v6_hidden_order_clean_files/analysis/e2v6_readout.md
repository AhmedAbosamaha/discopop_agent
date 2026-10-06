# E2-v6 — the read-out beside the registered tests

Every trial is judged as the registration says (`e2b1_stats.judge`): a **success** is a race-free verified parallel program whose parallel construct covers the hot loop; **unsafe** is a wrong output, a crash at the verification size, a race or a program that does not compile; the speed check is off in every setup, so FASTER (at least 1.1×) is reported beside the successes. A model alone has no gate: its parallel programs are race-checked afterwards (`checks/e2v6_race_check`).

## The five units whose order is hidden — every setup

Per unit: successes of the trials (of them FASTER) · unsafe; "too slow" = the output is right and a timed run did not end in 30 minutes (reported, not unsafe).

| setup | `k19` | `k23` | `k27` | `k31` | `s161` | all five | 95 % interval |
|---|---|---|---|---|---|---|---|
| Haiku agent, evidence, one attempt | 10/10 (10) · 0 unsafe | 9/10 (9) · 0 unsafe | 6/10 (6) · 0 unsafe | 10/10 (10) · 0 unsafe | 10/10 (10) · 0 unsafe | **45/50** (45) · 0 unsafe | 79–96 % |
| Haiku agent, no evidence, one attempt | 0/10 (0) · 0 unsafe | 1/10 (0) · 0 unsafe | 0/10 (0) · 0 unsafe | 0/10 (0) · 0 unsafe | 9/10 (8) · 0 unsafe | **10/50** (8) · 0 unsafe | 11–33 % |
| Haiku agent, evidence, three attempts | 10/10 (10) · 0 unsafe | 8/10 (8) · 1 unsafe | 8/10 (8) · 0 unsafe | 10/10 (10) · 0 unsafe | 10/10 (10) · 0 unsafe | **46/50** (46) · 1 unsafe | 81–97 % |
| Haiku agent, no evidence, three attempts | 2/10 (2) · 0 unsafe | 4/10 (4) · 0 unsafe | 1/10 (0) · 0 unsafe | 5/10 (5) · 0 unsafe | 10/10 (7) · 0 unsafe | **22/50** (18) · 0 unsafe | 31–58 % |
| Haiku alone | 0/10 (0) · 10 unsafe | 0/10 (0) · 10 unsafe | 0/10 (0) · 10 unsafe | 0/10 (0) · 10 unsafe | 3/10 (3) · 7 unsafe | **3/50** (3) · 47 unsafe | 2–16 % |
| Sonnet 5 alone | 0/5 (0) · 4 unsafe | 0/5 (0) · 5 unsafe | 0/5 (0) · 5 unsafe | 2/5 (2) · 3 unsafe | 5/5 (5) · 0 unsafe | **7/25** (7) · 17 unsafe | 14–48 % |
| Opus 5.5 alone | 0/5 (0) · 1 unsafe · 4 too slow | 0/5 (0) · 5 unsafe | 0/5 (0) · 0 unsafe · 5 too slow | 5/5 (3) · 0 unsafe | 5/5 (5) · 0 unsafe | **10/25** (8) · 6 unsafe · 9 too slow | 23–59 % |
| Fable 5.1 alone | 4/5 (0) · 0 unsafe · 1 too slow | 0/5 (0) · 5 unsafe | 3/5 (0) · 2 unsafe | 5/5 (5) · 0 unsafe | 5/5 (5) · 0 unsafe | **17/25** (10) · 7 unsafe · 1 too slow | 48–83 % |

## How fast the successes are — beside the expert version

A success only has to be parallel, right and race-free: the speed check is off. Median speedup of the successes over the original (the larger of 6 and 12 threads), lowest to highest, and how many; the last row is the expert version of the unit through the same verification (`t0_14_c2_refs`; `s161` has none).

| setup | `k19` | `k23` | `k27` | `k31` | `s161` | `k48` |
|---|---|---|---|---|---|---|
| Haiku agent, evidence, one attempt | 1.45× (1.31–1.54, 10) | 1.40× (1.37–1.47, 9) | 1.93× (1.75–2.00, 6) | 1.37× (1.22–1.39, 10) | 2.15× (1.88–2.23, 10) | 3.80× (3.62–4.04, 10) |
| Haiku agent, no evidence, one attempt | — | 0.65× (0.65–0.65, 1) | — | — | 2.15× (0.66–2.24, 9) | 3.77× (3.66–4.08, 10) |
| Haiku agent, evidence, three attempts | 1.51× (1.37–1.54, 10) | 1.39× (1.25–1.46, 8) | 1.99× (1.94–2.04, 8) | 1.37× (1.31–1.38, 10) | 2.19× (2.01–2.23, 10) | 3.34× (3.20–4.34, 10) |
| Haiku agent, no evidence, three attempts | 3.27× (1.51–5.04, 2) | 1.45× (1.44–1.46, 4) | 0.66× (0.66–0.66, 1) | 1.36× (1.35–1.37, 5) | 1.99× (0.36–2.25, 10) | 3.33× (3.22–4.17, 10) |
| Haiku alone | — | — | — | — | 2.15× (1.66–2.16, 3) | 3.87× (3.87–3.87, 1) |
| Sonnet 5 alone | — | — | — | 3.05× (3.02–3.08, 2) | 3.77× (1.33–3.84, 5) | — |
| Opus 5.5 alone | — | — | — | 2.27× (1.00–2.45, 5) | 1.71× (1.66–2.26, 5) | 0.01× (0.01–0.01, 4) |
| Fable 5.1 alone | 0.14× (0.01–1.00, 4) | — | 0.01× (0.01–0.01, 3) | 2.30× (2.27–3.17, 5) | 2.17× (2.02–2.24, 5) | 0.49× (0.01–0.94, 5) |
| **expert version** | 4.14× | 3.33× | 4.17× | 3.09× | — | 4.13× |

## The agent's four setups against each other

Pooled over the five units, stratified by unit: Mantel-Haenszel odds ratio (95 % RBG interval), the Cochran-Mantel-Haenszel p with the continuity correction and the exact conditional p. The two registered tests are one-sided as predicted and are `e2b1_stats.py`'s (`stats/v6_i`, `stats/v6_ii`); they are repeated here from this tool's own tables as a cross-check. The others are descriptive and two-sided.

| contrast (X against Y) | X | Y | MH odds ratio | CMH p | exact p | per unit X vs Y (Fisher two-sided) |
|---|---|---|---|---|---|---|
| V6-i (registered, confirmatory): evidence against none, one attempt | 45/50 | 10/50 | 351.00 (26.20–4702.21) | 7.77e-14 one-sided | 1.35e-16 | `k19` 10/10 vs 0/10 (1.08e-05); `k23` 9/10 vs 1/10 (0.00109); `k27` 6/10 vs 0/10 (0.0108); `k31` 10/10 vs 0/10 (1.08e-05); `s161` 10/10 vs 9/10 (1) |
| V6-ii (registered): without evidence, three attempts against one | 22/50 | 10/50 | 21.00 (2.36–187.00) | 0.000678 one-sided | 0.000342 | `k19` 2/10 vs 0/10 (0.474); `k23` 4/10 vs 1/10 (0.303); `k27` 1/10 vs 0/10 (1); `k31` 5/10 vs 0/10 (0.0325); `s161` 10/10 vs 9/10 (1) |
| descriptive 1: three attempts without evidence against one attempt with it | 22/50 | 45/50 | 0.03 (0.01–0.16) | 3.33e-07 two-sided | 6.25e-08 | `k19` 2/10 vs 10/10 (0.000714); `k23` 4/10 vs 9/10 (0.0573); `k27` 1/10 vs 6/10 (0.0573); `k31` 5/10 vs 10/10 (0.0325); `s161` 10/10 vs 10/10 (1) |
| descriptive 2: with evidence, three attempts against one | 46/50 | 45/50 | 1.33 (0.30–5.91) | 1 two-sided | 1 | `k19` 10/10 vs 10/10 (1); `k23` 8/10 vs 9/10 (1); `k27` 8/10 vs 6/10 (0.628); `k31` 10/10 vs 10/10 (1); `s161` 10/10 vs 10/10 (1) |
| descriptive: evidence against none, three attempts | 46/50 | 22/50 | 25.00 (6.13–102.00) | 1.6e-07 two-sided | 3.36e-08 | `k19` 10/10 vs 2/10 (0.000714); `k23` 8/10 vs 4/10 (0.17); `k27` 8/10 vs 1/10 (0.00548); `k31` 10/10 vs 5/10 (0.0325); `s161` 10/10 vs 10/10 (1) |

**The interaction (H5b's form: extra attempts help most where the evidence is absent).** Two more attempts raise the success rate by +24 points without evidence (10/50 → 22/50) and by +2 with it (45/50 → 46/50). Ratio of the two Mantel-Haenszel odds ratios 15.75 (95 % 1.12–221.83), z = 2.04, one-sided p = 0.0205. Descriptive.

## Model calls and cost

Over the five units: model calls, calls per trial and per success; API-equivalent cost of all seven units of the setup (the runs were paid by subscription).

| setup | trials (five units) | model calls | per trial | per success | cost, all seven units | agent time, all seven |
|---|---|---|---|---|---|---|
| Haiku agent, evidence, one attempt | 50 | 73 | 1.46 | 1.6 | $15.81 | 4.6 h |
| Haiku agent, no evidence, one attempt | 50 | 146 | 2.92 | 14.6 | $17.75 | 4.9 h |
| Haiku agent, evidence, three attempts | 50 | 105 | 2.10 | 2.3 | $47.24 | 7.0 h |
| Haiku agent, no evidence, three attempts | 50 | 392 | 7.84 | 17.8 | $112.07 | 14.7 h |
| Haiku alone | 50 | 50 | 1.00 | 16.7 | $6.17 | 1.9 h |
| Sonnet 5 alone | 25 | 25 | 1.00 | 3.6 | $11.76 | 2.5 h |
| Opus 5.5 alone | 25 | 25 | 1.00 | 2.5 | $7.27 | 0.5 h |
| Fable 5.1 alone | 25 | 25 | 1.00 | 1.5 | $24.65 | 1.1 h |

All setups, all seven units: 1181 model calls, $242.72 API-equivalent.

## The control `k48` — the order in the file is right

| setup | successes (FASTER) | unsafe | too slow | trials |
|---|---|---|---|---|
| Haiku agent, evidence, one attempt | 10 (10) | 0 | 0 | 10 |
| Haiku agent, no evidence, one attempt | 10 (10) | 0 | 0 | 10 |
| Haiku agent, evidence, three attempts | 10 (10) | 0 | 0 | 10 |
| Haiku agent, no evidence, three attempts | 10 (10) | 0 | 0 | 10 |
| Haiku alone | 1 (1) | 9 | 0 | 10 |
| Sonnet 5 alone | 0 (0) | 5 | 0 | 5 |
| Opus 5.5 alone | 4 (0) | 0 | 1 | 5 |
| Fable 5.1 alone | 5 (0) | 0 | 0 | 5 |

## The decline unit `k53` — the statements feed each other: the loop has to be left alone

Nothing can be gained on this unit; the efficient answer is the unchanged program. A program that is parallel all the same is right only if the kernel's iterations still run in their order — because the loop over the index tables stays outside every parallel region (only a loop the program added is parallel), or because the program orders the iterations at run time from the tables (an inspector that sorts them into levels: right for any tables, and here close to one level per iteration). Per setup: trials that ship a parallel program at all; of those, wrong (unsafe) and too slow; and where the loop over the index tables stands, as the program's text shows.

| setup | trials | left unchanged or not parallel | ship a parallel program | of those unsafe | too slow | index-table loop inside a parallel region | index-table loop outside every parallel region (an added loop is parallel) |
|---|---|---|---|---|---|---|---|
| Haiku agent, evidence, one attempt | 10 | 10 | 0 | 0 | 0 | 0 | 0 |
| Haiku agent, no evidence, one attempt | 10 | 10 | 0 | 0 | 0 | 0 | 0 |
| Haiku agent, evidence, three attempts | 10 | 6 | 4 | 2 | 0 | 0 | 4 |
| Haiku agent, no evidence, three attempts | 10 | 6 | 4 | 0 | 0 | 0 | 4 |
| Haiku alone | 10 | 0 | 10 | 10 | 0 | 10 | 0 |
| Sonnet 5 alone | 5 | 0 | 5 | 5 | 0 | 5 | 0 |
| Opus 5.5 alone | 5 | 0 | 5 | 0 | 1 | 5 | 0 |
| Fable 5.1 alone | 5 | 0 | 5 | 0 | 0 | 5 | 0 |

## Every unsafe program of the agent

| setup | unit | repetition | what the harness recorded |
|---|---|---|---|
| Haiku agent, evidence, three attempts | `k23` | 10 | BROKEN: the final run at 6 threads ended with return code -11 after 1.7 s |
| Haiku agent, evidence, three attempts | `k53` | 10 | BROKEN: the final run at 6 threads ended with return code -11 after 1.2 s |
| Haiku agent, evidence, three attempts | `k53` | 3 | BROKEN: the final run at 6 threads ended with return code -11 after 1.2 s |

3 of the agent's 280 trials with a verdict.

## What the changed programs did to the repetition loop, and where they keep temporary data

Read from the text of every shipped program that differs from the original, all seven units. "Automatic array": a local array of the data's length (`real_t x[LEN_1D]` inside the function) — it lies on the stack, as does every thread's `private` or `firstprivate` copy of it; the data is larger at the size the final check runs than at the size a setup works with.

| setup | changed programs | repetition loop kept as it is | temporary data: automatic array | heap | static | none | automatic array: unsafe · success · other |
|---|---|---|---|---|---|---|---|
| Haiku agent, evidence, one attempt | 55 | 55 | 0 | 0 | 0 | 55 | 0 · 0 · 0 |
| Haiku agent, no evidence, one attempt | 20 | 20 | 0 | 2 | 0 | 18 | 0 · 0 · 0 |
| Haiku agent, evidence, three attempts | 61 | 61 | 3 | 2 | 0 | 56 | 3 · 0 · 0 |
| Haiku agent, no evidence, three attempts | 36 | 36 | 0 | 8 | 0 | 28 | 0 · 0 · 0 |
| Haiku alone | 70 | 70 | 0 | 4 | 0 | 66 | 0 · 0 · 0 |
| Sonnet 5 alone | 35 | 35 | 0 | 6 | 0 | 29 | 0 · 0 · 0 |
| Opus 5.5 alone | 35 | 33 | 0 | 25 | 0 | 10 | 0 · 0 · 0 |
| Fable 5.1 alone | 35 | 29 | 0 | 25 | 0 | 10 | 0 · 0 · 0 |

The agent's programs that changed the repetition loop or hold an automatic array:

- Haiku agent, evidence, three attempts — automatic array: k23 rep 10: c_snapshot, d_snapshot — in a private clause (BROKEN)
- Haiku agent, evidence, three attempts — automatic array: k53 rep 10: u_snapshot — in a private clause (BROKEN)
- Haiku agent, evidence, three attempts — automatic array: k53 rep 3: v_work — in a private clause (BROKEN)

