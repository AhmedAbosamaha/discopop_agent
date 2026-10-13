# E8 (restructuring depth) — what the saved trials already say about a deeper level

Built by `depth_from_the_archive.py`. No model, nothing run: every number is read from saved trials that ran at depth 0. A region counted here is one the agent listed after an accepted rewrite and skipped only because of the depth limit — the region a run at depth 1 would have sent to the model.

**The kinds below were defined on 13 Oct 2026, after the logs had been read** (the script's head has the rule). A description of the archive, not a registered measure.

## The pragma experiment, the 18 loops — the corrected table

| setup | trials | a rewrite accepted | a deeper level would ask the model | — only about the repetition loop and the function | — also about another loop | loops with such a trial |
|---|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 90 | 80 | 80 of 80 | 76 | 4 | `s252` (2), `s331` (2) |
| the model writes | 90 | 84 | 20 of 84 | 20 | 0 | — |

The regions a deeper level would send to the model, by kind:

| setup | regions | the repetition loop | the function | a loop around a parallel one | a loop inside a parallel one | a loop beside them |
|---|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 164 | 80 (80 asked about before, at depth 0) | 80 (7 asked about before, at depth 0) | 0 | 0 | 4 |
| the model writes | 40 | 20 (20 asked about before, at depth 0) | 20 (4 asked about before, at depth 0) | 0 | 0 | 0 |

The trials themselves (outcomes as the harness verified them; the speed verdict is the agent's own on a rewrite without a pragma — "not faster than before the rewrite" sends the model back to try again):

| setup | trials | FASTER | model calls | median per trial | cost | per call | full re-profiles | trials with a rewrite sent back as not faster | how those trials ended |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 90 | 75 | 320 | 2.0 | $52.08 | $0.163 | 227 | 38 of 90 (76 verdicts) | FASTER 25, no-change 10, parallel-not-faster 3 |
| the model writes | 90 | 80 | 295 | 2.0 | $45.65 | $0.155 | 84 | 0 of 90 (0 verdicts) | — |

## The pragma experiment, the 18 loops — as first run

| setup | trials | a rewrite accepted | a deeper level would ask the model | — only about the repetition loop and the function | — also about another loop | loops with such a trial |
|---|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 90 | 81 | 81 of 81 | 76 | 5 | `s252` (2), `s331` (2), `s341` (1) |
| the model writes | 90 | 85 | 21 of 85 | 20 | 1 | `s341` (1) |

The regions a deeper level would send to the model, by kind:

| setup | regions | the repetition loop | the function | a loop around a parallel one | a loop inside a parallel one | a loop beside them |
|---|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 167 | 81 (81 asked about before, at depth 0) | 81 (8 asked about before, at depth 0) | 0 | 0 | 5 |
| the model writes | 42 | 20 (20 asked about before, at depth 0) | 21 (5 asked about before, at depth 0) | 0 | 0 | 1 |

The trials themselves (outcomes as the harness verified them; the speed verdict is the agent's own on a rewrite without a pragma — "not faster than before the rewrite" sends the model back to try again):

| setup | trials | FASTER | model calls | median per trial | cost | per call | full re-profiles | trials with a rewrite sent back as not faster | how those trials ended |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 90 | 76 | 320 | 2.0 | $51.75 | $0.162 | 227 | 38 of 90 (94 verdicts) | FASTER 26, no-change 9, parallel-not-faster 3 |
| the model writes | 90 | 81 | 294 | 2.0 | $45.80 | $0.156 | 85 | 0 of 90 (0 verdicts) | — |

## The contrast set, the six loops under test — the corrected table

| setup | trials | a rewrite accepted | a deeper level would ask the model | — only about the repetition loop and the function | — also about another loop | loops with such a trial |
|---|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 30 | 26 | 26 of 26 | 14 | 12 | `s3113` (1), `s314` (2), `s315` (2), `s316` (2), `s318` (5) |
| the model writes | 30 | 30 | 3 of 30 | 0 | 3 | `s315` (2), `s318` (1) |

The regions a deeper level would send to the model, by kind:

| setup | regions | the repetition loop | the function | a loop around a parallel one | a loop inside a parallel one | a loop beside them |
|---|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 64 | 26 (26 asked about before, at depth 0) | 26 (9 asked about before, at depth 0) | 0 | 6 | 6 |
| the model writes | 6 | 0 (0 asked about before, at depth 0) | 3 (0 asked about before, at depth 0) | 0 | 3 | 0 |

The trials themselves (outcomes as the harness verified them; the speed verdict is the agent's own on a rewrite without a pragma — "not faster than before the rewrite" sends the model back to try again):

| setup | trials | FASTER | model calls | median per trial | cost | per call | full re-profiles | trials with a rewrite sent back as not faster | how those trials ended |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 30 | 25 | 138 | 4.0 | $22.04 | $0.160 | 113 | 9 of 30 (12 verdicts) | FASTER 8, no-change 1 |
| the model writes | 30 | 30 | 44 | 1.0 | $5.06 | $0.115 | 28 | 0 of 30 (0 verdicts) | — |

## The main comparison, the 18 loops — as first run (an earlier version of the texts)

| setup | trials | a rewrite accepted | a deeper level would ask the model | — only about the repetition loop and the function | — also about another loop | loops with such a trial |
|---|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 90 | 88 | 88 of 88 | 72 | 16 | `s252` (3), `s281` (5), `s331` (4), `s341` (4) |

The regions a deeper level would send to the model, by kind:

| setup | regions | the repetition loop | the function | a loop around a parallel one | a loop inside a parallel one | a loop beside them |
|---|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 187 | 83 (83 asked about before, at depth 0) | 88 (14 asked about before, at depth 0) | 0 | 4 | 12 |

The trials themselves (outcomes as the harness verified them; the speed verdict is the agent's own on a rewrite without a pragma — "not faster than before the rewrite" sends the model back to try again):

| setup | trials | FASTER | model calls | median per trial | cost | per call | full re-profiles | trials with a rewrite sent back as not faster | how those trials ended |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DiscoPoP writes | 90 | 73 | 259 | 2.0 | $40.07 | $0.155 | 178 | 28 of 90 (60 verdicts) | FASTER 21, no-change 4, parallel-not-faster 3 |

## Every other loop a deeper level would have sent to the model

Not the repetition loop and not the function. The premise of the depth experiment — a rewrite leaves or exposes another task — holds only for the loops *beside* the parallel ones; a loop *inside* a loop that is about to be parallel has nothing left to win.

- **the pragma experiment, the 18 loops** (the corrected table), DiscoPoP writes: `e3_r_2` `s252` rep4, the trial ended parallel-not-faster — a loop beside them, lines 15–18:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              a[i] = prod[i] + t;
              t = prod[i];
          }
  ```

- **the pragma experiment, the 18 loops** (the corrected table), DiscoPoP writes: `e3_r_2` `s252` rep5, the trial ended parallel-not-faster — a loop beside them, lines 15–18:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              a[i] = s[i] + t;
              t = s[i];
          }
  ```

- **the pragma experiment, the 18 loops** (the corrected table), DiscoPoP writes: `e3_r_4` `s331` rep2, the trial ended FASTER — a loop beside them, lines 18–22:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              if (matches[i]) {
                  j = i;
              }
          }
  ```

- **the pragma experiment, the 18 loops** (the corrected table), DiscoPoP writes: `e3_r_4` `s331` rep3, the trial ended parallel-not-faster — a loop beside them, lines 14–18:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              if (matches[i]) {
                  j = i;
              }
          }
  ```

- **the pragma experiment, the 18 loops** (as first run), DiscoPoP writes: `e3_r_2` `s252` rep4, the trial ended parallel-not-faster — a loop beside them, lines 15–18:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              a[i] = prod[i] + t;
              t = prod[i];
          }
  ```

- **the pragma experiment, the 18 loops** (as first run), DiscoPoP writes: `e3_r_2` `s252` rep5, the trial ended parallel-not-faster — a loop beside them, lines 15–18:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              a[i] = s[i] + t;
              t = s[i];
          }
  ```

- **the pragma experiment, the 18 loops** (as first run), DiscoPoP writes: `e3_r_4` `s341` rep5, the trial ended FASTER — a loop beside them, lines 9–14:

  ```c
      for (int i = 0; i < LEN_1D; i++) {
          rank[i] = count;
          if (b[i] > (real_t)0.) {
              count++;
          }
      }
  ```

- **the pragma experiment, the 18 loops** (as first run), DiscoPoP writes: `e3_r_4` `s331` rep2, the trial ended FASTER — a loop beside them, lines 18–22:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              if (matches[i]) {
                  j = i;
              }
          }
  ```

- **the pragma experiment, the 18 loops** (as first run), DiscoPoP writes: `e3_r_4` `s331` rep3, the trial ended parallel-not-faster — a loop beside them, lines 14–18:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              if (matches[i]) {
                  j = i;
              }
          }
  ```

- **the pragma experiment, the 18 loops** (as first run), the model writes: `e3_r_4` `s341` rep5, the trial ended FASTER — a loop beside them, lines 10–15:

  ```c
      for (int i = 0; i < LEN_1D; i++) {
          prefix[i] = count;
          if (b[i] > (real_t)0.) {
              count++;
          }
      }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3b_1` `s314` rep3, the trial ended FASTER — a loop inside a parallel one, lines 21–25:

  ```c
              for (int i = start + 1; i < end; i++) {
                  if (a[i] > chunk_max[chunk]) {
                      chunk_max[chunk] = a[i];
                  }
              }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3b_1` `s314` rep4, the trial ended FASTER — a loop inside a parallel one, lines 16–20:

  ```c
              for (int i = c * chunk_size + 1; i < end; i++) {
                  if (a[i] > local_max) {
                      local_max = a[i];
                  }
              }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3b_2` `s3113` rep3, the trial ended FASTER — a loop inside a parallel one, lines 16–20:

  ```c
              for (int i = start + 1; i < end; i++) {
                  if ((ABS(a[i])) > block_max[block]) {
                      block_max[block] = ABS(a[i]);
                  }
              }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3b_3` `s315` rep1, the trial ended FASTER — a loop beside them, lines 23–28:

  ```c
          for (int i = 1; i < LEN_1D; ++i) {
              if (vals[i] > x) {
                  x = vals[i];
                  index = indices[i];
              }
          }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3b_3` `s315` rep5, the trial ended FASTER — a loop inside a parallel one, lines 25–30:

  ```c
              for (int i = start; i < end; i++) {
                  if (a[i] > local_max[chunk]) {
                      local_max[chunk] = a[i];
                      local_index[chunk] = i;
                  }
              }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3b_4` `s318` rep1, the trial ended parallel-not-faster — a loop beside them, lines 19–24:

  ```c
          for (int i = 1; i < LEN_1D; i++) {
              if (vals[i] > max) {
                  max = vals[i];
                  index = i;
              }
          }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3b_4` `s318` rep2, the trial ended FASTER — a loop beside them, lines 19–24:

  ```c
          for (int i = 1; i < LEN_1D; i++) {
              if (abs_vals[i] > max) {
                  max = abs_vals[i];
                  index = i;
              }
          }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3b_4` `s318` rep3, the trial ended FASTER — a loop beside them, lines 19–24:

  ```c
          for (int i = 1; i < LEN_1D; i++) {
              if (abs_vals[i] > max) {
                  index = i;
                  max = abs_vals[i];
              }
          }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3b_4` `s318` rep4, the trial ended FASTER — a loop beside them, lines 20–25:

  ```c
          for (int i = 0; i < LEN_1D - 1; i++) {
              if (vals[i] > max) {
                  max = vals[i];
                  index = i + 1;
              }
          }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3b_4` `s318` rep5, the trial ended FASTER — a loop beside them, lines 14–19:

  ```c
          for (int i = 1; i < LEN_1D; i++) {
              int k = i * inc;
              if (ABS(a[k]) == max) {
                  index = i;
              }
          }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3bc_s316` `s316` rep1, the trial ended FASTER — a loop inside a parallel one, lines 21–23:

  ```c
                  for (int i = start + 1; i < end; ++i) {
                      m = a[i] < m ? a[i] : m;
                  }
  ```

- **the contrast set, the six loops under test** (the corrected table), DiscoPoP writes: `e3bc_s316` `s316` rep3, the trial ended FASTER — a loop inside a parallel one, lines 17–21:

  ```c
              for (int i = start + 1; i < end; ++i) {
                  if (a[i] < min_in_chunk) {
                      min_in_chunk = a[i];
                  }
              }
  ```

- **the contrast set, the six loops under test** (the corrected table), the model writes: `e3b_3` `s315` rep2, the trial ended FASTER — a loop inside a parallel one, lines 20–25:

  ```c
          for (int i = 0; i < LEN_1D; ++i) {
              if (a[i] == x) {
                  index = i;
                  break;
              }
          }
  ```

- **the contrast set, the six loops under test** (the corrected table), the model writes: `e3b_3` `s315` rep5, the trial ended FASTER — a loop inside a parallel one, lines 19–24:

  ```c
          for (int i = 0; i < LEN_1D; ++i) {
              if (a[i] == x) {
                  index = i;
                  break;
              }
          }
  ```

- **the contrast set, the six loops under test** (the corrected table), the model writes: `e3b_4` `s318` rep4, the trial ended FASTER — a loop inside a parallel one, lines 24–30:

  ```c
          for (int i = 1; i < LEN_1D; i++) {
              k = i * inc;
              if (ABS(a[k]) == max) {
                  index = i;
                  break;
              }
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_2` `s252` rep1, the trial ended parallel-not-faster — a loop beside them, lines 18–21:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              a[i] = s_vals[i] + t;
              t = s_vals[i];
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_2` `s252` rep2, the trial ended parallel-not-faster — a loop beside them, lines 16–20:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              real_t s = products[i];
              a[i] = s + t;
              t = s;
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_2` `s252` rep4, the trial ended parallel-not-faster — a loop beside them, lines 17–20:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              a[i] = s[i] + t;
              t = s[i];
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_3` `s281` rep1, the trial ended parallel-not-faster — a loop beside them, lines 18–22:

  ```c
          for (int i = (LEN_1D + 1) / 2; i < LEN_1D; i++) {
              x = a[LEN_1D-i-1] + b[i] * c[i];
              a[i] = x-(real_t)1.0;
              b[i] = x;
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_3` `s281` rep2, the trial ended parallel-not-faster — a loop beside them, lines 13–17:

  ```c
          for (int i = mid; i < LEN_1D; i++) {
              x = a[LEN_1D-i-1] + b[i] * c[i];
              a[i] = x-(real_t)1.0;
              b[i] = x;
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_3` `s281` rep3, the trial ended parallel-not-faster — a loop beside them, lines 14–18:

  ```c
          for (int i = (LEN_1D-1)/2+1; i < LEN_1D; i++) {
              x = a[LEN_1D-i-1] + b[i] * c[i];
              a[i] = x-(real_t)1.0;
              b[i] = x;
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_3` `s281` rep4, the trial ended FASTER — a loop beside them, lines 12–16:

  ```c
          for (int i = LEN_1D / 2; i < LEN_1D; i++) {
              x = a[LEN_1D-i-1] + b[i] * c[i];
              a[i] = x-(real_t)1.0;
              b[i] = x;
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_3` `s281` rep5, the trial ended no-change — a loop beside them, lines 12–16:

  ```c
          for (int i = LEN_1D / 2; i < LEN_1D; i++) {
              x = a[LEN_1D-i-1] + b[i] * c[i];
              a[i] = x-(real_t)1.0;
              b[i] = x;
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_4` `s331` rep1, the trial ended FASTER — a loop inside a parallel one, lines 9–15:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              if (a[i] < (real_t)0.) {
                  if (i > j_local) {
                      j_local = i;
                  }
              }
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_4` `s331` rep2, the trial ended no-change — a loop inside a parallel one, lines 9–13:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              if (a[i] < (real_t)0.) {
                  j = i > j ? i : j;
              }
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_4` `s331` rep4, the trial ended no-change — a loop inside a parallel one, lines 10–14:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              if (a[i] < (real_t)0.) {
                  j = (i > j) ? i : j;
              }
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_4` `s331` rep5, the trial ended no-change — a loop inside a parallel one, lines 11–17:

  ```c
          for (int i = 0; i < LEN_1D; i++) {
              if (a[i] < (real_t)0.) {
                  if (i > j) {
                      j = i;
                  }
              }
          }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_4` `s341` rep1, the trial ended FASTER — a loop beside them, lines 11–16:

  ```c
      for (int i = 0; i < LEN_1D; i++) {
          if (b[i] > (real_t)0.) {
              indices[i] = idx;
              idx++;
          }
      }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_4` `s341` rep3, the trial ended FASTER — a loop beside them, lines 10–15:

  ```c
      for (int i = 0; i < LEN_1D; i++) {
          if (b[i] > (real_t)0.) {
              indices[i] = count;
              count++;
          }
      }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_4` `s341` rep4, the trial ended FASTER — a loop beside them, lines 11–16:

  ```c
      for (int i = 0; i < LEN_1D; i++) {
          prefix[i+1] = prefix[i];
          if (b[i] > (real_t)0.) {
              prefix[i+1]++;
          }
      }
  ```

- **the main comparison, the 18 loops** (as first run (an earlier version of the texts)), DiscoPoP writes: `e1v6_r_4` `s341` rep5, the trial ended FASTER — a loop beside them, lines 9–11:

  ```c
      for (int i = 0; i < LEN_1D; i++) {
          count[i + 1] = count[i] + (b[i] > (real_t)0. ? 1 : 0);
      }
  ```

## Checks on this read-out

- trials whose file could not be rebuilt, or whose listed loop is no loop in the rebuilt file: 0
- trials with a failed model call or run with the depth flag (they would not belong here): 0

