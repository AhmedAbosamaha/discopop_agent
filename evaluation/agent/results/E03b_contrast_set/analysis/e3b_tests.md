# E3b — the pre-registered test (the loops under test of the contrast set)

Registered in THESIS_EXPERIMENTS §6 on 10 Oct 2026, before any of E3b's trials. One-sided as registered; one test, a new member of the campaign's family: the bound is p × 53.

| test | hypothesis | p (one-sided) | family bound | verdict | detail |
|---|---|---:|---:|---|---|
| E3b-1 | more race-free FASTER trials where the model writes the pragma than where DiscoPoP writes it (CMH stratified by loop) | 0.0135 | 0.715 | supported | the model writes 30 of 30, DiscoPoP writes 24 of 30; 3 loop(s) differ (s315, s316, s318); 3 informative loop(s); the normal approximation does not hold (Mantel-Fleiss) — read the exact p; Mantel-Haenszel odds ratio infinite (no loop with a trial against the model's setup); exact conditional p 0.00926; unusable programs over all trials: 0 of 35 where the model writes, 0 of 35 where DiscoPoP writes |

## Per loop under test: race-free FASTER trials

| loop | DiscoPoP writes | the model writes | Haiku alone |
|---|---:|---:|---:|
| `s3113` | 5 of 5 | 5 of 5 | 5 of 5 |
| `s314` | 5 of 5 | 5 of 5 | 5 of 5 |
| `s315` | 2 of 5 | 5 of 5 | 4 of 5 |
| `s316` | 3 of 5 | 5 of 5 | 4 of 5 |
| `s318` | 4 of 5 | 5 of 5 | 4 of 5 |
| `s319` | 5 of 5 | 5 of 5 | 5 of 5 |

## The three-way table per setup

| loops | setup | race-free FASTER | verified parallel | unusable (BROKEN · slower · racy · not compiling) |
|---|---|---:|---:|---|
| under test | DiscoPoP alone | 0 of 30 | 0 | **0** (0 · 0 · 0 · 0) |
| under test | the agent, DiscoPoP writes the pragma | 24 of 30 | 25 | **0** (0 · 0 · 0 · 0) |
| under test | the agent, the model writes the pragma | 30 of 30 | 30 | **0** (0 · 0 · 0 · 0) |
| under test | Haiku alone | 27 of 30 | 28 | **3** (2 · 0 · 1 · 0) |
| control | DiscoPoP alone | 5 of 5 | 5 | **0** (0 · 0 · 0 · 0) |
| control | the agent, DiscoPoP writes the pragma | 5 of 5 | 5 | **0** (0 · 0 · 0 · 0) |
| control | the agent, the model writes the pragma | 5 of 5 | 5 | **0** (0 · 0 · 0 · 0) |
| control | Haiku alone | 5 of 5 | 5 | **0** (0 · 0 · 0 · 0) |

**Unusable programs shipped by the agent where DiscoPoP writes the pragma: 0 of 35** — none.

**Unusable programs shipped by the agent where the model writes the pragma: 0 of 35** — none.
