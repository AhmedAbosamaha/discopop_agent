# E2-B1 — hand-read of every unit (measured condition 6; 27 Sep 2026)

Read from the packages as generated (`prepared/tsvc_b1/*`, `prepared/rodinia_b1/bfs`, their headers under
`prepared/_harness/`), before the T0.11 draws. For each unit the questions are the same.

- What does the model's file show?
- Where does the deciding fact sit? Tier 1 means outside the hot loop's function. Tier 2 means in that
  function.
- Is the fact out of the model's reach?
- What should the measured conditions give?

**What no model can read.** Every arm's model has only Read, Edit and Write. Those tools are held to the
workspace by a hook: Fix 95, `llm/providers.py`, `confine_to`. Bash, Glob, Grep and the web are blocked
outright. The harness header lies outside every workspace (D39), so its contents are out of reach. A model
sees only its name in the `#include`, which says nothing about the unit (`tsvc_b1/s161.h`). No source
carries solution vocabulary: `test_integrity` §1b checks all 228 sources.

**Common to every unit.** The hot loop is the one `hot_loop` names in meta.json (record §6, 27 Sep). It is
verbatim from TSVC-2 or Rodinia. `pb_mix` changes a few input elements between repetitions, so the
repetition loop is sequential by a true dependence. The hot loop sits inside it.

## Direction (a): a hidden dependence

| unit | the model sees | the deciding fact, and where | what breaks a naive `parallel for` |
|---|---|---|---|
| s151 (tier 1) | `s151s(a, b, m)`: `a[i] = a[i + m] + b[i]`; the call `s151s(a, b,  1)` in the kernel | `m = 1` is the caller's argument, in another function of the same file | a WAR at distance 1 on `a`: iteration i reads `a[i+1]` before iteration i+1 overwrites it; a race, and a wrong result under most schedules |
| s161 (tier 1) | `if (b[i] < 0) goto L20; a[i] = …; goto L10; L20: c[i+1] = a[i] + d[i]*d[i]` | b's sign pattern, set in the header (odd i negative) and not in the file | an odd iteration writes `c[i+1]` and the next (even) iteration reads it: a flow dependence at distance 1. `pb_mix` adds at most 0.25 once per element, so the signs never flip (magnitudes ≥ 0.75) |
| bfs (tier 1) | the frontier loop: for each frontier node `tid` and each edge, `id = h_graph_edges[i]`; `if (!h_graph_visited[id]) { h_cost[id] = h_cost[tid] + 1; h_updating_graph_mask[id] = true; }` | the edge list, generated in the header: frontier nodes share unvisited neighbours (validated: about half the hot loop's stores go to an element another iteration of the same level stored to) | write-write conflicts. They are of EQUAL values: every frontier node of a level has the same cost. The output is deterministic under the naive pragma (Rodinia's own OpenMP version ships it), so the gate fails it at the race check (TSan with archer), not on the output. A race-free parallel version needs atomics or a formulation without shared stores. The update loop after it is independent (the coverage check does not count it, criterion v2) |
| s131 (tier 2) | `int m = 1;` above the repetition loop; `a[i] = a[i + m] + b[i]` | `m`, in the same function | as s151 |
| s424 (tier 2) | `int vl = 63; xx = flat_2d_array + vl;` then `xx[i+1] = flat_2d_array[i] + a[i]` | the alias of `xx` into `flat_2d_array`, set in the same function. Both are header globals, and `xx` has no `restrict` (restrict on an alias would be undefined behaviour) | a flow dependence at distance 64: iteration i stores `flat_2d_array[i+64]`, which iteration i+64 reads. The coverage check counts a write through either name (`aliases`, criterion v2) |

## Direction (b): a hidden independence (descriptive, the author's decision 1)

| unit | the model sees | the deciding fact, and where | why the loop is in fact independent |
|---|---|---|---|
| s152 | `b[i] = d[i] * e[i]; s152s(a, b, c, i);` | the callee's body, `a[i] += b[i] * c[i]`, another function of the file | each iteration touches element i only |
| s171 | `a[i * inc] += b[i]` | `inc`, a header global set to 1 by the harness (TSVC's main passes 1) | with inc = 1 every iteration updates its own `a[i]`. The text allows inc = 0 |
| s481 | `if (d[i] < 0) exit(0); a[i] += b[i] * c[i];` | d's values, set in the header, all positive (and never lowered by `pb_mix`) | no iteration exits; each updates its own `a[i]` |
| s258 | `real_t s;` in the kernel; `s = 0.;` per repetition; `if (a[i] > 0.) s = d[i]*d[i]; b[i] = s*c[i] + d[i]; e[i] = (s + 1.)*aa[0][i];` over `i < LEN_2D` | a's values, in the header, all positive (`pb_mix` only raises them) | s is set before every use in every iteration, so no value is carried and each iteration writes its own `b[i]`, `e[i]` — parallel with `s` private. Packaged with the recorded deviation (the author, 27 Sep): `LEN_2D` is `LEN_1D` and `aa` one row, both in the header; the text is TSVC's |
| s277 | the two guarded `goto`s, `a[i] += c[i]*d[i]`, and `b[i+1] = …` | a's values, in the header, all ≥ 0 (`pb_mix` only raises them) | the first test jumps past both updates in every iteration: the loop does no work, and the `b[i+1]`→`b[i]` flow the text shows never happens. Admitted by the author (27 Sep) |
| vas | `int * __restrict__ ip = pb_ip;` (TSVC's own declaration), `a[ip[i]] = b[i]` | `pb_ip` is a permutation, built in the header | no two iterations write the same element |
| s482 | `a[i] += b[i] * c[i]; if (c[i] > b[i]) break;` | c = b/2, set in the header, so the exit never fires | every iteration runs and updates its own `a[i]`. The screen predicts class R (a loop with a `break`), so it is expected to fail its measured condition (class A in T0.11). If it fails, the unit leaves with the reason and the next member of its group in source order enters |

**s258** was packaged after the author's ruling (27 Sep; the deviation in record §6), read the same way.

## Checks this reading asks of the measurements

- (a): `naive_pragma.py` fails the gate on all five units. For bfs it fails at the race check only
  (equal-value stores).
- (a): T0.11 gives class R; DiscoPoP's profile names the deciding dependence:
  - s151 and s131 on `a`;
  - s161 on `c`;
  - s424 on `flat_2d_array`/`xx`;
  - bfs on `h_cost`/`h_updating_graph_mask`.
- (b): T0.11 gives class A, with Do-All on the hot loop and DiscoPoP's pragma applied (`routing_check.py`,
  3 of 3). s482 is expected to fail this.
- Every unit: `routing_check.py` finds the hot loop in the candidate table at its declared line. That is
  the check that the profile covers the loop under study.
