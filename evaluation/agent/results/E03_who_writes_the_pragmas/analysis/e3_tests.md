# E3 — the two pre-registered tests (class R, 18 loops)

Registered in THESIS_EXPERIMENTS §6 (H6: 14 Sep; H6b: 23 Sep; both restated on 9 Oct 2026, before any of E3's trials). One-sided as registered; Holm over the two; the campaign family's bound is p × 52.

| test | hypothesis | p (one-sided) | Holm (E3) | family bound | verdict | detail |
|---|---|---:|---:|---:|---|---|
| E3-1 | H6 — more race-free FASTER trials where the model writes the pragma than where DiscoPoP writes it (CMH stratified by loop) | 0.142 | 0.283 | 1 | not established | the model writes 81 of 90, DiscoPoP writes 76 of 90; 7 loop(s) differ (s112, s211, s241, s243, s244, s252, s331); 8 informative loop(s); the normal approximation holds; Mantel-Haenszel odds ratio 2 (95 % 0.704–5.68); exact conditional p 0.14; unusable programs over all classes: 0 of 105 where the model writes, 0 of 105 where DiscoPoP writes |
| E3-2 | H6b — with the model writing, at least Haiku alone's race-free FASTER rate and nothing BROKEN; p is the refuting direction (Haiku alone ahead, Wilcoxon on the per-loop rates) | 1 | 1 | 1 | not refuted | the model writes 81 of 90, Haiku alone 38 of 90; the agent ahead on 15 loops, Haiku alone on 0; BROKEN trials of the setup on class R: 0, over all classes: 0 |

## Per loop (class R): race-free FASTER trials

| loop | DiscoPoP writes | the model writes | Haiku alone (E1-v6) |
|---|---:|---:|---:|
| `s112` | 5 of 5 | 4 of 5 | 0 of 5 |
| `s121` | 5 of 5 | 5 of 5 | 0 of 5 |
| `s1213` | 5 of 5 | 5 of 5 | 2 of 5 |
| `s127` | 5 of 5 | 5 of 5 | 5 of 5 |
| `s211` | 4 of 5 | 5 of 5 | 0 of 5 |
| `s212` | 5 of 5 | 5 of 5 | 2 of 5 |
| `s241` | 4 of 5 | 3 of 5 | 1 of 5 |
| `s243` | 5 of 5 | 4 of 5 | 2 of 5 |
| `s244` | 3 of 5 | 4 of 5 | 0 of 5 |
| `s252` | 3 of 5 | 5 of 5 | 3 of 5 |
| `s254` | 5 of 5 | 5 of 5 | 4 of 5 |
| `s255` | 5 of 5 | 5 of 5 | 3 of 5 |
| `s281` | 5 of 5 | 5 of 5 | 3 of 5 |
| `s291` | 5 of 5 | 5 of 5 | 4 of 5 |
| `s292` | 5 of 5 | 5 of 5 | 1 of 5 |
| `s293` | 5 of 5 | 5 of 5 | 2 of 5 |
| `s331` | 1 of 5 | 5 of 5 | 5 of 5 |
| `s341` | 1 of 5 | 1 of 5 | 1 of 5 |

## The three-way table per setup, by class

| class | setup | race-free FASTER | verified parallel | unusable (BROKEN · slower · racy · not compiling) |
|---|---|---:|---:|---|
| R | DiscoPoP alone | 0 of 90 | 0 | **0** (0 · 0 · 0 · 0) |
| R | the agent, DiscoPoP writes the pragma | 76 of 90 | 81 | **0** (0 · 0 · 0 · 0) |
| R | the agent, the model writes the pragma | 81 of 90 | 83 | **0** (0 · 0 · 0 · 0) |
| R | Haiku alone (E1-v6) | 38 of 90 | 53 | **50** (17 · 10 · 3 · 20) |
| D | DiscoPoP alone | 0 of 12 | 0 | **0** (0 · 0 · 0 · 0) |
| D | the agent, DiscoPoP writes the pragma | 0 of 12 | 0 | **0** (0 · 0 · 0 · 0) |
| D | the agent, the model writes the pragma | 0 of 12 | 0 | **0** (0 · 0 · 0 · 0) |
| D | Haiku alone (E1-v6) | 0 of 12 | 0 | **11** (8 · 0 · 0 · 3) |
| A | DiscoPoP alone | 3 of 3 | 3 | **0** (0 · 0 · 0 · 0) |
| A | the agent, DiscoPoP writes the pragma | 3 of 3 | 3 | **0** (0 · 0 · 0 · 0) |
| A | the agent, the model writes the pragma | 3 of 3 | 3 | **0** (0 · 0 · 0 · 0) |
| A | Haiku alone (E1-v6) | 2 of 3 | 2 | **1** (0 · 0 · 0 · 1) |

**Unusable programs shipped by the agent where DiscoPoP writes the pragma: 0 of 105** — none.

**Unusable programs shipped by the agent where the model writes the pragma: 0 of 105** — none.
