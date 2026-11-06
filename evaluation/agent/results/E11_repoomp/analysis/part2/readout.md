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
