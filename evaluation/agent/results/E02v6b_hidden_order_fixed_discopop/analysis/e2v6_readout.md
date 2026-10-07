# E2-v6b (E2-v6 on the fixed DiscoPoP; the models alone are E2-v6's) — the read-out beside the registered tests

Every trial is judged as the registration says (`e2b1_stats.judge`): a **success** is a race-free verified parallel program whose parallel construct covers the hot loop; **unsafe** is a wrong output, a crash at the verification size, a race or a program that does not compile; the speed check is off in every setup, so FASTER (at least 1.1×) is reported beside the successes. A model alone has no gate: its parallel programs are race-checked afterwards (`checks/e2v6_race_check`).

## The five units whose order is hidden — every setup

Per unit: successes of the trials (of them FASTER) · unsafe; "too slow" = the output is right and a timed run did not end in 30 minutes (reported, not unsafe).

| setup | `k19` | `k23` | `k27` | `k31` | `s161` | all five | 95 % interval |
|---|---|---|---|---|---|---|---|
| Haiku agent, evidence, one attempt | 10/10 (10) · 0 unsafe | 9/10 (9) · 0 unsafe | 5/10 (5) · 0 unsafe | 10/10 (10) · 0 unsafe | 10/10 (10) · 0 unsafe | **44/50** (44) · 0 unsafe | 76–94 % |
| Haiku agent, no evidence, one attempt | 0/10 (0) · 0 unsafe | 4/10 (3) · 0 unsafe | 0/10 (0) · 0 unsafe | 1/10 (0) · 0 unsafe | 9/10 (9) · 0 unsafe | **14/50** (12) · 0 unsafe | 17–42 % |
| Haiku agent, evidence, three attempts | 10/10 (10) · 0 unsafe | 8/10 (7) · 0 unsafe | 10/10 (8) · 0 unsafe | 10/10 (10) · 0 unsafe | 10/10 (9) · 0 unsafe | **48/50** (44) · 0 unsafe | 87–99 % |
| Haiku agent, no evidence, three attempts | 5/10 (5) · 0 unsafe | 4/10 (2) · 0 unsafe | 0/10 (0) · 0 unsafe | 3/10 (3) · 0 unsafe | 10/10 (10) · 0 unsafe | **22/50** (20) · 0 unsafe | 31–58 % |
| Haiku alone | 0/10 (0) · 10 unsafe | 0/10 (0) · 10 unsafe | 0/10 (0) · 10 unsafe | 0/10 (0) · 10 unsafe | 3/10 (3) · 7 unsafe | **3/50** (3) · 47 unsafe | 2–16 % |
| Sonnet 5 alone | 0/5 (0) · 4 unsafe | 0/5 (0) · 5 unsafe | 0/5 (0) · 5 unsafe | 2/5 (2) · 3 unsafe | 5/5 (5) · 0 unsafe | **7/25** (7) · 17 unsafe | 14–48 % |
| Opus 5.5 alone | 0/5 (0) · 1 unsafe · 4 too slow | 0/5 (0) · 5 unsafe | 0/5 (0) · 0 unsafe · 5 too slow | 5/5 (3) · 0 unsafe | 5/5 (5) · 0 unsafe | **10/25** (8) · 6 unsafe · 9 too slow | 23–59 % |
| Fable 5.1 alone | 4/5 (0) · 0 unsafe · 1 too slow | 0/5 (0) · 5 unsafe | 3/5 (0) · 2 unsafe | 5/5 (5) · 0 unsafe | 5/5 (5) · 0 unsafe | **17/25** (10) · 7 unsafe · 1 too slow | 48–83 % |

## How fast the successes are — beside the expert version

A success only has to be parallel, right and race-free: the speed check is off. Median speedup of the successes over the original (the larger of 6 and 12 threads), lowest to highest, and how many; the last row is the expert version of the unit through the same verification (`t0_14_c2_refs`; `s161` has none).

| setup | `k19` | `k23` | `k27` | `k31` | `s161` | `k48` |
|---|---|---|---|---|---|---|
| Haiku agent, evidence, one attempt | 4.07× (3.17–4.19, 10) | 3.27× (2.66–3.30, 9) | 4.04× (1.14–4.13, 5) | 3.06× (2.59–3.38, 10) | 2.14× (1.85–2.24, 10) | 3.85× (2.95–4.16, 10) |
| Haiku agent, no evidence, one attempt | — | 3.25× (0.62–3.28, 4) | — | 0.62× (0.62–0.62, 1) | 2.19× (2.06–2.24, 9) | 4.12× (3.84–4.17, 10) |
| Haiku agent, evidence, three attempts | 3.95× (3.62–4.28, 10) | 3.15× (0.33–3.50, 8) | 3.77× (1.05–4.23, 10) | 3.10× (2.98–3.35, 10) | 2.22× (0.28–2.30, 10) | 4.03× (3.68–4.14, 10) |
| Haiku agent, no evidence, three attempts | 4.05× (3.96–4.15, 5) | 1.97× (0.73–3.21, 4) | — | 2.80× (1.48–3.00, 3) | 2.22× (1.45–2.25, 10) | 3.85× (2.55–4.16, 10) |
| Haiku alone | — | — | — | — | 2.15× (1.66–2.16, 3) | 3.87× (3.87–3.87, 1) |
| Sonnet 5 alone | — | — | — | 3.05× (3.02–3.08, 2) | 3.77× (1.33–3.84, 5) | — |
| Opus 5.5 alone | — | — | — | 2.27× (1.00–2.45, 5) | 1.71× (1.66–2.26, 5) | 0.01× (0.01–0.01, 4) |
| Fable 5.1 alone | 0.14× (0.01–1.00, 4) | — | 0.01× (0.01–0.01, 3) | 2.30× (2.27–3.17, 5) | 2.17× (2.02–2.24, 5) | 0.49× (0.01–0.94, 5) |
| **expert version** | 4.14× | 3.33× | 4.17× | 3.09× | — | 4.13× |

## The agent's four setups against each other

Pooled over the five units, stratified by unit: Mantel-Haenszel odds ratio (95 % RBG interval), the Cochran-Mantel-Haenszel p with the continuity correction and the exact conditional p. The two registered tests are one-sided as predicted and are `e2b1_stats.py`'s (`stats/v6_i`, `stats/v6_ii`); they are repeated here from this tool's own tables as a cross-check. The others are descriptive and two-sided.

| contrast (X against Y) | X | Y | MH odds ratio | CMH p | exact p | per unit X vs Y (Fisher two-sided) |
|---|---|---|---|---|---|---|
| V6-i (registered, confirmatory): evidence against none, one attempt | 44/50 | 14/50 | 76.00 (11.06–522.01) | 5.57e-11 one-sided | 7.01e-13 | `k19` 10/10 vs 0/10 (1.08e-05); `k23` 9/10 vs 4/10 (0.0573); `k27` 5/10 vs 0/10 (0.0325); `k31` 10/10 vs 1/10 (0.000119); `s161` 10/10 vs 9/10 (1) |
| V6-ii (registered): without evidence, three attempts against one | 22/50 | 14/50 | 3.58 (1.08–11.88) | 0.0278 one-sided | 0.026 | `k19` 5/10 vs 0/10 (0.0325); `k23` 4/10 vs 4/10 (1); `k27` 0/10 vs 0/10 (1); `k31` 3/10 vs 1/10 (0.582); `s161` 10/10 vs 9/10 (1) |
| descriptive 1: three attempts without evidence against one attempt with it | 22/50 | 44/50 | 0.02 (0.00–0.16) | 5.07e-07 two-sided | 6.67e-08 | `k19` 5/10 vs 10/10 (0.0325); `k23` 4/10 vs 9/10 (0.0573); `k27` 0/10 vs 5/10 (0.0325); `k31` 3/10 vs 10/10 (0.0031); `s161` 10/10 vs 10/10 (1) |
| descriptive 2: with evidence, three attempts against one | 48/50 | 44/50 | 3.22 (0.65–15.97) | 0.244 two-sided | 0.238 | `k19` 10/10 vs 10/10 (1); `k23` 8/10 vs 9/10 (1); `k27` 10/10 vs 5/10 (0.0325); `k31` 10/10 vs 10/10 (1); `s161` 10/10 vs 10/10 (1) |
| descriptive: evidence against none, three attempts | 48/50 | 22/50 | 33.50 (7.27–154.38) | 1.02e-08 two-sided | 8.36e-10 | `k19` 10/10 vs 5/10 (0.0325); `k23` 8/10 vs 4/10 (0.17); `k27` 10/10 vs 0/10 (1.08e-05); `k31` 10/10 vs 3/10 (0.0031); `s161` 10/10 vs 10/10 (1) |

**The interaction (H5b's form: extra attempts help most where the evidence is absent).** Two more attempts raise the success rate by +16 points without evidence (14/50 → 22/50) and by +8 with it (44/50 → 48/50). Ratio of the two Mantel-Haenszel odds ratios 1.11 (95 % 0.15–8.21), z = 0.10, one-sided p = 0.459. Descriptive.

## Model calls and cost

Over the five units: model calls, calls per trial and per success; API-equivalent cost of all seven units of the setup (the runs were paid by subscription).

| setup | trials (five units) | model calls | per trial | per success | cost, all seven units | agent time, all seven |
|---|---|---|---|---|---|---|
| Haiku agent, evidence, one attempt | 50 | 89 | 1.78 | 2.0 | $17.43 | 5.3 h |
| Haiku agent, no evidence, one attempt | 50 | 145 | 2.90 | 10.4 | $16.73 | 4.9 h |
| Haiku agent, evidence, three attempts | 50 | 92 | 1.84 | 1.9 | $42.35 | 6.6 h |
| Haiku agent, no evidence, three attempts | 50 | 372 | 7.44 | 16.9 | $114.85 | 15.9 h |
| Haiku alone | 50 | 50 | 1.00 | 16.7 | $6.17 | 1.9 h |
| Sonnet 5 alone | 25 | 25 | 1.00 | 3.6 | $11.76 | 2.5 h |
| Opus 5.5 alone | 25 | 25 | 1.00 | 2.5 | $7.27 | 0.5 h |
| Fable 5.1 alone | 25 | 25 | 1.00 | 1.5 | $24.65 | 1.1 h |

All setups, all seven units: 1152 model calls, $241.20 API-equivalent.

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
| Haiku agent, evidence, three attempts | 10 | 4 | 6 | 0 | 0 | 0 | 6 |
| Haiku agent, no evidence, three attempts | 10 | 6 | 4 | 0 | 0 | 0 | 4 |
| Haiku alone | 10 | 0 | 10 | 10 | 0 | 10 | 0 |
| Sonnet 5 alone | 5 | 0 | 5 | 5 | 0 | 5 | 0 |
| Opus 5.5 alone | 5 | 0 | 5 | 0 | 1 | 5 | 0 |
| Fable 5.1 alone | 5 | 0 | 5 | 0 | 0 | 5 | 0 |

## Every unsafe program of the agent

None.

0 of the agent's 280 trials with a verdict.

## What the changed programs did to the repetition loop, and where they keep temporary data

Read from the text of every shipped program that differs from the original, all seven units. "Automatic array": a local array of the data's length (`real_t x[LEN_1D]` inside the function) — it lies on the stack, as does every thread's `private` or `firstprivate` copy of it; the data is larger at the size the final check runs than at the size a setup works with.

| setup | changed programs | repetition loop kept as it is | temporary data: automatic array | heap | static | none | automatic array: unsafe · success · other |
|---|---|---|---|---|---|---|---|
| Haiku agent, evidence, one attempt | 54 | 54 | 0 | 0 | 0 | 54 | 0 · 0 · 0 |
| Haiku agent, no evidence, one attempt | 24 | 24 | 0 | 2 | 0 | 22 | 0 · 0 · 0 |
| Haiku agent, evidence, three attempts | 66 | 65 | 0 | 10 | 0 | 56 | 0 · 0 · 0 |
| Haiku agent, no evidence, three attempts | 38 | 38 | 0 | 9 | 0 | 29 | 0 · 0 · 0 |
| Haiku alone | 70 | 70 | 0 | 4 | 0 | 66 | 0 · 0 · 0 |
| Sonnet 5 alone | 35 | 35 | 0 | 6 | 0 | 29 | 0 · 0 · 0 |
| Opus 5.5 alone | 35 | 33 | 0 | 25 | 0 | 10 | 0 · 0 · 0 |
| Fable 5.1 alone | 35 | 29 | 0 | 25 | 0 | 10 | 0 · 0 · 0 |

The agent's programs that changed the repetition loop or hold an automatic array:

- Haiku agent, evidence, three attempts — repetition loop: k23 rep 3: 4 repetition loops, a directive on the repetition loop (success)

