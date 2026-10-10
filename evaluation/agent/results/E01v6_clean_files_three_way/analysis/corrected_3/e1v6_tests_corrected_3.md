# E1-v6 — the nine pre-registered tests (class R, 18 loops, paired by loop)

Registered in THESIS_EXPERIMENTS §6, 5 Oct 2026, before any main trial. One-sided as registered; Holm over the nine; the campaign family's bound is p × 52. "no test": fewer than six loops differ.

| test | hypothesis | p (one-sided) | Holm (E1-v6) | family bound | rejected (Holm, 0.05) | detail |
|---|---|---:|---:|---:|---|---|
| T1 | H1 — the agent faster than DiscoPoP alone (per-loop medians) | 1.53e-05 | 0.000137 | 0.000793 | yes | 16 non-zero pairs of 18, median agent ÷ DiscoPoP alone 1.937× |
| T2 | H13 — fewer unusable programs than Haiku 4.5 alone | 0.000205 | 0.00164 | 0.0107 | yes | the agent ahead on 16 loops, Haiku 4.5 alone on 0; two-sided p 0.00041 |
| T3 | H13 — fewer unusable programs than Sonnet 5 alone | 1 | 1 | 1 | no | the agent ahead on 5 loops, Sonnet 5 alone on 0; fewer than 6 non-zero pairs: no test |
| T4 | H13 — fewer unusable programs than Opus 5.5 alone | 1 | 1 | 1 | no | the agent ahead on 0 loops, Opus 5.5 alone on 0; fewer than 6 non-zero pairs: no test |
| T5 | H13 — fewer unusable programs than Fable 5.1 alone | 1 | 1 | 1 | no | the agent ahead on 1 loops, Fable 5.1 alone on 0; fewer than 6 non-zero pairs: no test |
| T6 | reach — more race-free FASTER than Haiku 4.5 alone | 0.00402 | 0.0282 | 0.209 | yes | the agent ahead on 14 loops, Haiku 4.5 alone on 2; two-sided p 0.00805 |
| T7 | reach — more race-free FASTER than Sonnet 5 alone | 0.656 | 1 | 1 | no | the agent ahead on 3 loops, Sonnet 5 alone on 3; two-sided p 0.844 |
| T8 | reach — more race-free FASTER than Opus 5.5 alone | 1 | 1 | 1 | no | the agent ahead on 0 loops, Opus 5.5 alone on 4; fewer than 6 non-zero pairs: no test |
| T9 | reach — more race-free FASTER than Fable 5.1 alone | 1 | 1 | 1 | no | the agent ahead on 0 loops, Fable 5.1 alone on 4; fewer than 6 non-zero pairs: no test |

## The three-way table per model (class R, 90 trials per setup)

| setup | race-free FASTER | verified parallel | unusable (BROKEN · slower · racy · not compiling) |
|---|---:|---:|---|
| DiscoPoP alone | 0 of 90 | 0 | **0** (0 · 0 · 0 · 0) |
| DiscoPoP + agent | 75 of 90 | 81 | **0** (0 · 0 · 0 · 0) |
| Haiku 4.5 alone | 37 of 90 | 53 | **51** (16 · 11 · 3 · 21) |
| Sonnet 5 alone | 77 of 90 | 87 | **11** (3 · 3 · 5 · 0) |
| Opus 5.5 alone | 89 of 90 | 90 | **0** (0 · 0 · 0 · 0) |
| Fable 5.1 alone | 89 of 90 | 90 | **1** (0 · 1 · 0 · 0) |

**H2 (the agent ships no unusable program): 0 case(s)** — none.
