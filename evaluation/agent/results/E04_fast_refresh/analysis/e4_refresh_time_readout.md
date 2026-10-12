# E4 step 3 — what one fast refresh saves where the profiling run is long (`e4_refresh_time`), no model

Built by `e4_refresh_time_readout.py` from the run's records. Per program: the unchanged program profiled in full; one comment line put in front of the file; then, five times in turn, the fast refresh (from the profile before) and the full re-profile.

Commit `0038d1cdb`, the DiscoPoP pass `b22cb05f336e`; 2026-10-12T21:05:42Z to 2026-10-12T21:24:47Z.

## 1 Seconds of one refresh

Median of the five, with the smallest and the largest.

| program | lines of the file | full re-profile, s | fast refresh, s | saved, s | share of a full re-profile | pairs in which the fast refresh is shorter | fast refresh usable |
|---|---:|---:|---:|---:|---:|---:|---:|
| `rodinia-3.1/hotspot` | 331 | 108.2 (102.0–181.4) | 72.0 (52.2–109.2) | 35.6 (-0.7–129.3) | 33 % | 4 of 5 | 5 of 5 |
| `npb/is` | 812 | 41.2 (40.7–46.0) | 13.7 (13.5–14.3) | 27.0 (26.9–32.5) | 66 % | 5 of 5 | 5 of 5 |
| `burkardt/md` | 558 | 34.2 (33.6–34.7) | 12.9 (12.6–13.2) | 21.5 (20.4–21.8) | 63 % | 5 of 5 | 5 of 5 |
| `polybench/correlation` | 177 | 7.7 (7.2–7.9) | 3.5 (3.5–3.7) | 4.2 (3.5–4.3) | 54 % | 5 of 5 | 5 of 5 |

## 2 The parts

Medians of the five, seconds. The carrying over is what remains of a fast refresh beside its compile and its explorer run.

| program | full: compile | full: instrumented run | full: explorer | fast: compile | fast: explorer | fast: carrying over |
|---|---:|---:|---:|---:|---:|---:|
| `rodinia-3.1/hotspot` | 0.55 | 49.84 | 57.53 | 0.55 | 71.48 | 0.03 |
| `npb/is` | 0.54 | 27.67 | 12.99 | 0.54 | 13.11 | 0.06 |
| `burkardt/md` | 0.53 | 21.89 | 11.84 | 0.53 | 12.31 | 0.03 |
| `polybench/correlation` | 0.19 | 4.24 | 3.23 | 0.20 | 3.27 | 0.02 |

What the fast refresh carried over: `rodinia-3.1/hotspot` — 1115/1115 observed dependences carried forward (0 in rewritten code, 0 no longer present; 448 without callpath state), 8/8 loop trip counts; `npb/is` — 1060/1060 observed dependences carried forward (0 in rewritten code, 0 no longer present; 371 without callpath state), 22/22 loop trip counts; `burkardt/md` — 1722/1722 observed dependences carried forward (0 in rewritten code, 0 no longer present; 342 without callpath state), 17/17 loop trip counts; `polybench/correlation` — 532/532 observed dependences carried forward (0 in rewritten code, 0 no longer present; 207 without callpath state), 13/13 loop trip counts.

## 3 DiscoPoP's patterns after each

An unchanged program: the fast refresh should give the Do-All and reduction loops of the full profile, with the same clauses. Where the five full profiles differ among themselves, a difference from the fast refresh says nothing. Task patterns are counted apart: their number changes from one profile to the next and no directive of the agent comes from them.

| program | Do-All loops (first full profile) | reductions | different answers among the five full profiles | among the five fast refreshes | pairs with the same loops and clauses | fast refreshes equal to some full profile | task patterns, full | task patterns, fast |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `rodinia-3.1/hotspot` | 1 | 0 | 1 | 1 | 5 of 5 | 5 of 5 | 159–171 | 162–171 |
| `npb/is` | 13 | 0 | 1 | 1 | 5 of 5 | 5 of 5 | 24–24 | 24–24 |
| `burkardt/md` | 10 | 4 | 3 | 1 | 1 of 5 | 5 of 5 | 21–21 | 21–21 |
| `polybench/correlation` | 14 | 1 | 2 | 2 | 3 of 5 | 5 of 5 | 15–51 | 15–51 |

The explorer's own seconds over the eleven profiles of each program (five full, five fast, the one before): `rodinia-3.1/hotspot` 51.6 to 129.0; `npb/is` 12.8 to 13.7; `burkardt/md` 11.6 to 12.6; `polybench/correlation` 3.1 to 3.5.

## 4 As a share of an agent trial

The agent's trials of September on these programs (`history/E01_main_comparison`, arm `default`, the agent of that time): each trial's number of full re-profiles times the seconds saved by one fast refresh here, over the trial's duration.

| program | trials | trial duration, s | full re-profiles per trial | saved by one fast refresh, s | share of the trial | median |
|---|---:|---:|---:|---:|---:|---:|
| `rodinia-3.1/hotspot` | 5 | 683–1372 | 1–1 | 35.6 | 2.6–5.2 % | 4.5 % |
| `npb/is` | 5 | 1077–5400 | 2–7 | 27.0 | 1.5–7.5 % | 3.8 % |
| `burkardt/md` | 5 | 1670–2394 | 2–7 | 21.5 | 2.6–6.8 % | 6.3 % |

