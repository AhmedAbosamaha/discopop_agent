# E11 part 2 — the hidden-order kernels

Judged as E2-v6b judged its trials, every setup's race verdict from the race check (record §6, 6 Nov).

## Per unit

| unit | direction | setup | trials | success (FASTER) | unsafe | buckets |
|---|---|---|---|---|---|---|
| tsvc_c2/k19 | a | RepoOMP's release | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k19 | a | the agent | 5 | 5 (5) | 0 | success 5 |
| tsvc_c2/k19 | a | Sonnet 4.5 alone | 5 | 1 (1) | 4 | BROKEN 4, success 1 |
| tsvc_c2/k19 | a | DiscoPoP alone | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k23 | a | RepoOMP's release | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k23 | a | the agent | 5 | 5 (5) | 0 | success 5 |
| tsvc_c2/k23 | a | Sonnet 4.5 alone | 5 | 0 (0) | 5 | BROKEN 5 |
| tsvc_c2/k23 | a | DiscoPoP alone | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k27 | a | RepoOMP's release | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k27 | a | the agent | 5 | 3 (3) | 0 | no-change 2, success 3 |
| tsvc_c2/k27 | a | Sonnet 4.5 alone | 5 | 0 (0) | 5 | BROKEN 5 |
| tsvc_c2/k27 | a | DiscoPoP alone | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k31 | a | RepoOMP's release | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k31 | a | the agent | 5 | 5 (5) | 0 | success 5 |
| tsvc_c2/k31 | a | Sonnet 4.5 alone | 5 | 0 (0) | 5 | BROKEN 5 |
| tsvc_c2/k31 | a | DiscoPoP alone | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/s161 | a | RepoOMP's release | 5 | 0 (0) | 5 | racy 5 |
| tsvc_c2/s161 | a | the agent | 5 | 5 (5) | 0 | success 5 |
| tsvc_c2/s161 | a | Sonnet 4.5 alone | 5 | 2 (2) | 3 | BROKEN 3, success 2 |
| tsvc_c2/s161 | a | DiscoPoP alone | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k48 | b | RepoOMP's release | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k48 | b | the agent | 5 | 5 (5) | 0 | success 5 |
| tsvc_c2/k48 | b | Sonnet 4.5 alone | 5 | 5 (5) | 0 | success 5 |
| tsvc_c2/k48 | b | DiscoPoP alone | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k53 | decline | RepoOMP's release | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k53 | decline | the agent | 5 | 0 (0) | 0 | no-change 5 |
| tsvc_c2/k53 | decline | Sonnet 4.5 alone | 5 | 0 (0) | 5 | BROKEN 5 |
| tsvc_c2/k53 | decline | DiscoPoP alone | 5 | 0 (0) | 0 | no-change 5 |

## Direction (a), pooled

| setup | with a verdict | success | unsafe |
|---|---|---|---|
| RepoOMP's release | 25 | 0 [0–13 %] | 5 [9–39 %] |
| the agent | 25 | 23 [75–98 %] | 0 [0–13 %] |
| Sonnet 4.5 alone | 25 | 3 [4–30 %] | 22 [70–96 %] |
| DiscoPoP alone | 25 | 0 [0–13 %] | 0 [0–13 %] |

## The two tests (direction a, stratified by unit, one-sided, exact conditional p, Holm over the two)

| test | what | p exact | p Holm | MH odds ratio [95 %] |
|---|---|---|---|---|
| E11b-i | successes: the agent against RepoOMP's release | 2.1e-11 | 4.1e-11 | ∞ |
| E11b-ii | unsafe programs: RepoOMP's release against the agent | 0.004 | 0.004 | ∞ |

## RepoOMP's release at its three levels

Model: answered = at least one call answered; kept = primitive_adder's own validation kept a candidate; file = a CHANGED file reached the release's check; passed = that file passed it. An accepted copy is the release accepting a model file byte-equal to its input (timing noise).

| unit | trials | rules proposed | rules passed its check | model answered | kept by its validation | model file | passed its check | accepted (opt_method) | of which a copy | judged | its validation's reasons |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tsvc_c2/k19 | 5 | 0 | 0 | 5 | 4 | 4 | 0 | model 1, none 4 | 1 | no-change 5 | compile-fail-solo 2, shared-scalar-in-for(i) 2 |
| tsvc_c2/k23 | 5 | 5 | 0 | 5 | 0 | 0 | 0 | model 5 | 5 | no-change 5 | compile-fail-solo 1, shared-scalar-in-for(i) 14 |
| tsvc_c2/k27 | 5 | 0 | 0 | 5 | 5 | 5 | 0 | none 5 | 0 | no-change 5 | compile-fail-solo 1, shared-scalar-in-for(i) 1 |
| tsvc_c2/k31 | 5 | 5 | 0 | 5 | 0 | 0 | 0 | model 1, none 4 | 1 | no-change 5 | compile-fail-solo 2, shared-scalar-in-for(i) 13 |
| tsvc_c2/s161 | 5 | 0 | 0 | 5 | 5 | 5 | 5 | model 5 | 0 | racy 5 | — |
| tsvc_c2/k48 | 5 | 0 | 0 | 5 | 5 | 5 | 0 | none 5 | 0 | no-change 5 | shared-scalar-in-for(i) 1 |
| tsvc_c2/k53 | 5 | 0 | 0 | 5 | 5 | 5 | 0 | none 5 | 0 | no-change 5 | — |

## The hot loop by hand

- RepoOMP's release: parallel-as-written 5
- the agent: other 1, split-reordered 22, split-textual 5
- Sonnet 4.5 alone: other 2, parallel-as-written 7, split-reordered 3, split-textual 23

## Model calls and cost

| setup | trials | calls | cost (USD) |
|---|---|---|---|
| RepoOMP's release | 35 | 197 | 2.66 |
| the agent | 35 | 126 | 68.82 |
| Sonnet 4.5 alone | 35 | 35 | 7.63 |
| DiscoPoP alone | 35 | 0 | 0.00 |

## The speed of what was shipped (descriptive; added 11 Nov 2026, not pre-registered)

Speedup over the original as the harness measured it at the verification size: the median over a setup's successful trials of a unit, and apart over its racy programs. A setup that shipped the original program has no row.

| unit | setup | programs | median at 6 threads (lowest–highest) | median at 12 threads (lowest–highest) |
|---|---|---|---|---|
| tsvc_c2/k19 | the agent | 5 successes | 1.49× (1.48–3.94) | 2.32× (2.28–4.26) |
| tsvc_c2/k19 | Sonnet 4.5 alone | 1 success | 0.83× (0.83–0.83) | 1.18× (1.18–1.18) |
| tsvc_c2/k23 | the agent | 5 successes | 3.37× (2.37–3.74) | 3.41× (2.61–4.15) |
| tsvc_c2/k27 | the agent | 3 successes | 3.94× (1.95–4.12) | 4.19× (2.80–4.24) |
| tsvc_c2/k31 | the agent | 5 successes | 3.18× (3.11–3.29) | 3.26× (3.06–3.32) |
| tsvc_c2/s161 | RepoOMP's release | 5 racy | 3.77× (3.72–3.83) | 3.96× (3.63–4.02) |
| tsvc_c2/s161 | the agent | 5 successes | 2.27× (2.22–2.34) | 2.27× (2.20–2.30) |
| tsvc_c2/s161 | Sonnet 4.5 alone | 2 successes | 1.97× (1.87–2.07) | 2.25× (2.10–2.40) |
| tsvc_c2/k48 | the agent | 5 successes | 1.50× (1.33–3.84) | 2.37× (2.07–4.08) |
| tsvc_c2/k48 | Sonnet 4.5 alone | 5 successes | 1.48× (1.47–1.50) | 2.38× (2.36–2.40) |

Direction (a), the five units pooled, successes only:

- the agent: 23 successes, 3.11× at 6 threads, 3.24× at 12 threads.
- Sonnet 4.5 alone: 3 successes, 1.87× at 6 threads, 2.10× at 12 threads.
