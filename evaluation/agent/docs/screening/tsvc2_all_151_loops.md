# TSVC-2 screen: all 151 loop functions

I screened all 151 loop functions read-only and did not build, run or profile anything. The table has one row per `time_function` call at tsvc.c:3968–4118, and its names match that list exactly. 33 rows are marked "packaged" and 118 are not. Classes are predictions from the code alone. I did not use any `meta.json` class or measured result. The record also asks for measured checks (THESIS_EXPERIMENTS.md:1850); those come later and nothing here claims them:
- T0.11: the class, from three DiscoPoP draws.
- T0.10 / T0.13: the checks behind C1.
- For E2-B1: DiscoPoP naming the deciding dependence, and the routing pre-check.
- For E8: the DiscoPoP check after each step.

Sources read: `benchmarks/TSVC_2/src/tsvc.c` (4121 lines), `src/common.c` (`init()` at common.c:157–185, `initialise_arrays()` at common.c:187–763, `calc_checksum()` at common.c:765–1035) and `agent/tools/prepare_tsvc.py`.

## Legend

**Properties**
- **C1**: predicted class R, and the expert form changes code beyond pragmas and clauses.
- **H13**: the naive `#pragma omp parallel for` with default sharing would be wrong. Values:
  - "yes (race / changed output)".
  - "compile error": a `break` or `goto` leaves an `omp for`.
  - "no".
  - "no (data-cond.)": correct only because of the data fact named in the row.
- **E2a / E2b**: E2-B1 (a) hidden dependence / (b) hidden independence. Each row says where the deciding fact sits as shipped, then **pkg→** where the packager would put it.
- **E3**: needs a construct DiscoPoP cannot generate. **E3-ctrl**: an in-pattern `+`/`*` reduction, used as a control.
- **E8**: two dependent restructuring steps.
  - **strict**: after step 1 alone, DiscoPoP should still find no pattern in the hot region (the record's test).
  - **partial**: step 1 alone already gives a pattern on part of the hot region.
  - **weak**: both steps are needed, but step 2 does not act on code step 1 created, or step 1 alone already parallelizes the bulk.
- **A / D**: control classes.

**Predicted class**
- **A**: DiscoPoP alone should reach a correct pragma (Do-All, a `+ - * & | ^` reduction, private scalars).
- **A(inner, N-trip)**: only a fine-grained inner Do-All exists as written, so C1 depends on T0.11.
- **R**: DiscoPoP alone cannot parallelize the hot loop.
- **R(clause)**: R, but the fix is only a clause (for example `reduction(max:)`), so it is not C1.
- **D**: true recurrence with no faster form accepted (the record's convention).
- **data-cond.**: the class holds only for TSVC's shipped data.

**What the packager does today.** It builds only heap arrays `a..e` of `double`. It copies the code between `gettimeofday(t1)` and the repetition loop as declarations, and the repetition body verbatim. It returns the loop's `return` expression, or `(real_t)0` where TSVC returns `calc_checksum`. Its digest prints only `result` and `a..e`.

**Packaging codes**
- **pkg**: already in `agent/prepared/tsvc/`.
- **ok**: works with the packager as it is; only a `Loop` entry is needed.
- **pre(v)**: `v` is set before `t1`, either from `main` through `func_args` or as a constant. The packager's `pre` puts it in the kernel's first lines. That moves a fact that sits in another function into the same function.
- **glob(v)**: recommended instead of `pre` for a value that decides a dependence. The value lives in the harness's `init_array`, like the probes' `pb_ip` (prepare_tsvc.py:375–380).
- **2D**: needs `aa/bb/cc [LEN_2D][LEN_2D]`, a `LEN_2D` define with a `-D` size ladder, and those arrays in the digest. `LEN_2D` is not defined in the harness.
- **flat**: needs `flat_2d_array` and its digest.
- **x**: needs the global `x` and its digest.
- **xx**: needs the global `xx` (and `yy`), with `__restrict__` dropped (see s421).
- **ip**: uses the existing `pb_ip`.
- **indx**: needs `indx` with `init()`'s values.
- **init(…)**: TSVC's data property must be reproduced via `init_extra`, or the property is lost.
- **ret**: the returned expression must change so it carries the loop's result.
- **ABS**: define `ABS`; the harness does not have it.
- **fn(f)**: a file-scope callee passed via `globals_`, as for s4121's `f`.
- **regex**: `_tsvc_function` cannot find the function.
- **L2D-trip**: the trip count is `LEN_2D` over 1-D arrays, so the `LEN_1D` ladder does not size it.
- **no-init**: the loop has no `initialise_arrays` branch. In TSVC it inherits the previous loop's state; once packaged, the packager's own initialisation runs instead.
- **pun**: an argument is read through `int*` from a `real_t`. Under TSVC's `float`, `1.0f` reads as 1065353216. Under the packager's `double`, the low word of `1.0` reads as 0. "Verbatim" cannot be reproduced, so the author must choose the value.

**Shared by every row (not repeated in the rows)**
- The licence permits redistribution (benchmarks/TSVC_2/license.txt, UIUC/NCSA-style).
- Plain C, CPU only.
- Output is deterministic once the harness digest is added.
- Each package is a single file with one kernel.
- Size is set by `LEN_1D` through the packager's `-D<SIZE>_DATASET` ladder (prepare_tsvc.py:69–70), unless the row says 2D or L2D-trip.
- D26 risk is low for 1-D O(N) loops. The record notes random explorer stalls on s291, s3112, s322 and s331 (THESIS_EXPERIMENTS.md:1832); the timeout handles them.

**Marker oddities.** Rows are grouped in file order by the `// %x.y` comments.
- s000 has no marker.
- s258 has no marker and sits under %2.5.
- s261 sits under `%2.7`, but its comment says "scalar and array expansion".
- The markers %2.10, %2.12 and %2.11 appear in that order.
- %4.1 has no loop.
- %4.8 appears twice (tsvc.c:3382 and 3384).

## Linear dependence testing (s000, %1.1)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s000 | tsvc.c:57 | `a[i] = b[i] + 1;` | A: elementwise; H13 no | A | pragma | pkg | IN ctrl-A (packaged) | — |
| TSVC-2 | s111 | tsvc.c:78–79 | `for (i=1; i<N; i+=2) a[i] = a[i-1] + b[i];` | A: odd i writes; even i is read and never written (visible in the stride); H13 no | A | pragma | ok | IN ctrl-A | s000 |
| TSVC-2 | s1111 | tsvc.c:98–99 | `a[2*i] = c[i]*b[i] + d[i]*b[i] + …;` | A; H13 no | A | pragma | ok; no-init | IN ctrl-A | s000 |
| TSVC-2 | s112 | tsvc.c:120–121 | `for (i=N-2; i>=0; i--) a[i+1] = a[i] + b[i];` | C1: the reversed loop reads a[i] before iteration i-1 rewrites it (anti-dep); H13 yes | R | copy old a, then Do-All (reference exists) | pkg | IN C1/E1, H13 (packaged) | s121 (fix: copy) |
| TSVC-2 | s1112 | tsvc.c:140–141 | `a[i] = b[i] + 1.;` (reverse) | A; H13 no | A | pragma | ok; no-init | IN ctrl-A | s000 |
| TSVC-2 | s113 | tsvc.c:162–163 | `for (i=1…) a[i] = a[0] + b[i];` | A: a[0] is never written (i starts at 1, visible); H13 no | A | pragma | ok | IN ctrl-A (contrast to s293) | s000 |
| TSVC-2 | s1113 | tsvc.c:182–183 | `a[i] = a[LEN_1D/2] + b[i];` | C1: iteration N/2 rewrites a[N/2], which later iterations read; H13 yes (changed output) | R | index-set split: t0=a[N/2]; t1=t0+b[N/2]; Do-All over i≤N/2 with t0, Do-All over i>N/2 with t1 (bit-exact) | ok; no-init | IN C1/E1, H13 | s281 (index-set split) |
| TSVC-2 | s114 | tsvc.c:205–207 | `for j<i: aa[i][j] = aa[j][i] + bb[i][j];` | A: writes the lower triangle, reads the upper; outer i Do-All; H13 no | A (outer, triangular) | pragma + `schedule(dynamic)` | 2D | IN ctrl-A | — |
| TSVC-2 | s115 | tsvc.c:229–231 | `for j: for i>j: a[i] -= aa[j][i] * a[j];` | outer j carries a true dependence (a[j] is final at step j); inner i Do-All, ≤255 trips; H13 yes on the outer loop | A(inner, ≤255-trip) / D | inner pragma only (forward substitution; no coarse form) | 2D; L2D-trip | IN ctrl-D (T0.11 decides whether it is A(inner)) | s118 |
| TSVC-2 | s1115 | tsvc.c:251–253 | `aa[i][j] = aa[i][j]*cc[j][i] + bb[i][j];` | A: reads cc transposed, not aa; H13 no | A | pragma | 2D; no-init | IN ctrl-A | s000 |
| TSVC-2 | s116 | tsvc.c:274–279 | `a[i] = a[i+1]*a[i]; … a[i+4] = a[i+5]*a[i+4]; (i+=5)` | C1: block i reads a[i+5], the next block's first element, before that block writes it (anti-dep); H13 yes | R | copy old a (or save each block's a[i+5]) | ok; init: TSVC's a=1 (common.c:230) makes every product 1, so the output cannot show a race; with the packager's values, keep reps ≤8 (products grow or shrink geometrically) | IN C1/E1, H13 | s121 |
| TSVC-2 | s118 | tsvc.c:300–302 | `for j<i: a[i] += bb[j][i] * a[i-j-1];` | D: a[i] needs every earlier a; inner j is a `+` reduction of ≤255 terms; H13 yes | D | decline (the inner reduction is too fine) | 2D; L2D-trip | IN ctrl-D | s321 |
| TSVC-2 | s119 | tsvc.c:324–326 | `aa[i][j] = aa[i-1][j-1] + bb[i][j];` | outer i carries (1,1); inner j Do-All; H13 yes on the outer loop | A(inner, 255-trip) | inner pragma | 2D | IN ctrl-A(inner) | — |
| TSVC-2 | s1119 | tsvc.c:346–348 | `aa[i][j] = aa[i-1][j] + bb[i][j];` | inner j Do-All; interchange gives an outer j Do-All; H13 yes on the outer loop | A(inner, 256-trip); C1 conditional | interchange (j outer, one step) if the inner pragma is not faster | 2D; no-init | IN ctrl-A(inner); C1 only if T0.11 says R | s119 |

## Induction variable recognition (%1.2)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s121 | tsvc.c:371–373 | `j = i + 1; a[i] = a[j] + b[i];` | C1: anti-dep on a[i+1]; H13 yes | R | copy old a | pkg | IN C1/E1, H13 (packaged) | — (anchor: copy) |
| TSVC-2 | s122 | tsvc.c:402–404 | `for (i=n1-1; i<N; i+=n3) { k += j; a[i] += b[LEN_1D-k]; }` | C1: the scalar k is carried; H13 yes (k shared); E2 no (n1 and n3 only fix the closed form) | R | induction substitution k=(i-n1+1)/n3+1 (j=1), then Do-All | pre(n1=n3=1 from main tsvc.c:3983, read at :391–393) | IN C1/E1, H13 | s127 |
| TSVC-2 | s123 | tsvc.c:428–434 | `j++; a[j] = …; if (c[i] > 0.) { j++; a[j] = …; }` | C1; H13 yes; E3 (scan of counts); E8 (generic data); E2b weak: c=1 in initialise_arrays (common.c:246, another function and file) makes the branch always true, so j is fixed at 2i and 2i+1; pkg→ init_array (another function) | R | generic: count c>0 per chunk, exclusive scan of the counts, then write at the offsets (s341's three phases). The closed form j=2i(+1) is valid only if every c>0 | init (the packager's c is also >0, so the loop degenerates to s127; the generic path needs a sign mix, the author's choice) | IN C1/E1, H13, E8, E2b(weak) | s341 |
| TSVC-2 | s124 | tsvc.c:457–464 | `if (b[i] > 0.) { j++; a[j] = …; } else { j++; a[j] = …; }` | C1: j is carried but gets +1 on both branches, so j=i; H13 yes | R | substitute j=i | ok | IN C1/E1, H13 | s127 |
| TSVC-2 | s125 | tsvc.c:486–489 | `k++; flat_2d_array[k] = aa[i][j] + bb[i][j]*cc[i][j];` | C1: k is carried across the nest; H13 yes | R | k=i*LEN_2D+j, then collapse or an outer Do-All | 2D, flat, ret (the checksum is over flat) | IN C1/E1, H13 | s127 |
| TSVC-2 | s126 | tsvc.c:512–517 | `bb[j][i] = bb[j-1][i] + flat_2d_array[k-1]*cc[j][i]; ++k;` | C1: k is carried; inner j is a true column recurrence; outer i is independent once k is substituted; H13 yes | R | k=i*LEN_2D+j, then outer i Do-All | 2D, flat | IN C1/E1, H13 | s125 |
| TSVC-2 | s127 | tsvc.c:540–544 | `j++; a[j] = b[i]+c[i]*d[i]; j++; a[j] = b[i]+d[i]*e[i];` | C1: j is carried; H13 yes | R | write a[2i] and a[2i+1] directly | pkg | IN C1/E1, H13 (packaged) | — (anchor: induction) |
| TSVC-2 | s128 | tsvc.c:568–572 | `k = j+1; a[i] = b[k]-d[i]; j = k+1; b[k] = a[i]+c[k];` | C1: coupled inductions; H13 yes | R | k=2i, then Do-All | ok | IN C1/E1, H13 | s127 |

## Global data flow analysis (%1.3)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s131 | tsvc.c:593–594 | `a[i] = a[i + m] + b[i];` | C1: anti-dep; H13 yes; E2a weak: `m = 1` is set in the same function, one line above the repetition loop (tsvc.c:591, after t1); pkg→ copied as a declaration in the same place | R | copy old a | ok | IN C1/E1, H13, E2a(weak) | s121 (fix) |
| TSVC-2 | s132 | tsvc.c:617–618 | `aa[j][i] = aa[k][i-1] + b[i]*c[1];` | A; E2b weak: `j = m = 0` and `k = m+1 = 1` (tsvc.c:613–615, same function, 2–4 lines above) put writes and reads in different rows. The text would be a recurrence along i if j==k. H13 no (data-cond.) | A | pragma | 2D; L2D-trip (b) | IN ctrl-A, E2b(weak) | s431 |

## Nonlinear dependence testing (%1.4)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s141 | tsvc.c:641–645 | `k = …; for j≥i: { flat_2d_array[k] += bb[j][i]; k += j+1; }` | A: the packed index k(i,j)=j(j+1)/2+i is distinct for every i≤j (visible in the loop's own statements); k is reset for each i; H13 yes (k is declared at function scope, :639) | A (outer, private k) | `private(k)` + schedule | 2D, flat | IN ctrl-A | s251 |

## Interprocedural data flow analysis (%1.5)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s151 | tsvc.c:659–660 (callee `s151s`), call :674 | `a[i] = a[i + m] + b[i];` inside `s151s(a, b, 1)` | C1; H13 yes; **E2a strong**: the distance m is the literal `1`, passed from ANOTHER function (caller tsvc.c:674 → callee tsvc.c:657); pkg→ unchanged if s151s stays a separate function and the call keeps its literal | R | copy old a | fn(s151s; its parameters `a` and `b` shadow the globals) | IN C1/E1, H13, E2a | s121 (fix); s131 (property, weaker) |
| TSVC-2 | s152 | tsvc.c:699–701 + callee :686 | `b[i] = d[i]*e[i]; s152s(a, b, c, i);` (the callee does `a[i] += b[i]*c[i]`) | A; **E2b**: that the call touches only index i is decided in another function (tsvc.c:684–687); pkg→ unchanged via fn; H13 no | A | pragma | fn(s152s) | IN ctrl-A, E2b | s4121 |

## Control flow (%1.6)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s161 | tsvc.c:723–730 | `if (b[i] < 0.) goto L20; a[i] = c[i]+d[i]*e[i]; goto L10; L20: c[i+1] = a[i]+d[i]*d[i];` | C1; H13 yes (with TSVC data); **E2a strong**: the c[i+1]→c[i] flow across iterations exists only where b[i]<0 and b[i+1]≥0. b's sign pattern is set in initialise_arrays (common.c:296–297), in another function and file. `set_1d_array` walks `length` elements at the stride (common.c:144–146), so only b[0..N/2) alternates (even +1, odd −1). The upper half inherits positive values from s152 and always takes the else branch. pkg→ init_array (another function) | R | guarded distribution: loop 1 over b[i]<0 does `c[i+1]=a[i]+d[i]*d[i]`, then loop 2 over b[i]≥0 does `a[i]=c[i]+d[i]*e[i]`; both Do-All, bit-exact | init (b[0..N/2) alternating ±1, upper half positive): the packager's default b>0 never takes the branch, so the property is lost | IN C1/E1, H13, E2a | s1213 (fix: distribution) |
| TSVC-2 | s1161 | tsvc.c:752–759 | `if (c[i] < 0.) goto L20; a[i] = c[i]+…; … L20: b[i] = a[i]+d[i]*d[i];` | A: every statement touches index i only; H13 no | A | pragma | ok; no-init | IN ctrl-A | s000 |
| TSVC-2 | s162 | tsvc.c:784–786 | `if (k > 0) for: a[i] = a[i + k] + b[i]*c[i];` | C1; H13 yes; E2 no: the guard k>0 one line above already fixes the anti-dependence; k=1 from main (tsvc.c:3997) only sets its distance | R | copy old a | pre(k) | IN C1/E1, H13 | s121 |

## Symbolics (%1.7)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s171 | tsvc.c:811–812 | `a[i * inc] += b[i];` | A (data-cond.); **E2b strong**: inc=1 comes from main (tsvc.c:3998; n1 at :3961; read at :805), another function. With inc=0 every iteration would update a[0]. H13 no (data-cond.). pkg→ `pre` would move it to the kernel's first line, which weakens it; use glob(inc) | A | pragma | glob(inc) recommended | IN ctrl-A, E2b | — |
| TSVC-2 | s172 | tsvc.c:837–838 | `for (i=n1-1; i<N; i+=n3) a[i] += b[i];` | A: each iteration touches only a[i] (visible for any n3≠0); E2 no; H13 no | A | pragma | pre(n1, n3) | IN ctrl-A | s000 |
| TSVC-2 | s173 | tsvc.c:859–860 | `a[i+k] = a[i] + b[i];` (i<N/2) | A; E2b weak: `k = LEN_1D/2`, one line above the repetition loop (tsvc.c:857), keeps writes in [N/2,N) apart from reads in [0,N/2). A smaller k would carry a flow dependence. H13 no (data-cond.) | A | pragma | ok | IN ctrl-A, E2b(weak) | s132 |
| TSVC-2 | s174 | tsvc.c:884–885 | `for (i<M) a[i+M] = a[i] + b[i];` | A: disjoint for any M, because the bound and the offset are the same variable (visible); E2 no; H13 no | A | pragma | pre(M=LEN_1D/2, main :4001) | IN ctrl-A | s173 |
| TSVC-2 | s175 | tsvc.c:909–910 | `for (i+=inc) a[i] = a[i + inc] + b[i];` | C1; H13 yes; anti-dep for every inc≥1 (visible); E2 no | R | copy old a | pre(inc=1) | IN C1/E1, H13 | s121 |
| TSVC-2 | s176 | tsvc.c:932–934 | `for j: for i<m: a[i] += b[i+m-j-1] * c[j];` | inner i Do-All (m=N/2 trips); outer j accumulates into all of a; C1 conditional; H13 yes on outer j | A(inner) | interchange (i outer, j inner; keeps each a[i]'s summation order, bit-exact). E3 alternative: an array reduction on outer j | ok; O(N²/4) per repetition, so it needs a small profiling size (D26); TSVC's repetition count is 4*(iterations/LEN_1D) | IN ctrl-A(inner); C1 only if T0.11 says R | — |

## Statement reordering (%2.1)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s211 | tsvc.c:962–964 | `a[i] = b[i-1] + c[i]*d[i]; b[i] = b[i+1] - e[i]*d[i];` | C1: flow on b[i-1] plus anti-dep on b[i+1]; H13 yes | R | copy b, then distribute (b loop, then a loop) | pkg | IN C1/E1, H13 (packaged) | — (anchor: fission + copy) |
| TSVC-2 | s212 | tsvc.c:985–987 | `a[i] *= c[i]; b[i] += a[i + 1] * d[i];` | C1: anti-dep on a[i+1]; H13 yes | R | reorder or distribute (b loop first) | pkg | IN C1/E1, H13 (packaged) | s1213 |
| TSVC-2 | s1213 | tsvc.c:1006–1008 | `a[i] = b[i-1]+c[i]; b[i] = a[i+1]*d[i];` | C1: a cycle of flow on b[i-1] and anti on a[i+1]; H13 yes | R | distribute: b loop, then a loop | pkg (no-init in TSVC) | IN C1/E1, H13 (packaged) | — (anchor: distribution) |

## Loop distribution (%2.2)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s221 | tsvc.c:1029–1031 | `a[i] += c[i]*d[i]; b[i] = b[i-1] + a[i] + d[i];` | C1; H13 yes; E3 (scan); **E8 depth 1, partial** (after step 1 the a-loop is Do-All) | R | Step 1: distribute into a Do-All a-loop and the b-loop. Step 2 works on the b-loop that step 1 isolated: it is a prefix sum of (a[i]+d[i]), so it becomes a parallel scan. The scan is either three-phase (chunk sums, scan of the sums, fix-up) or `omp scan` with `reduction(inscan,+:)`; I did not verify that clang-20 accepts the latter. Step 1 alone gives a pattern on the a-loop only, and the hot recurrence stays serial. The scan reassociates the additions (double tolerance) | ok | IN C1/E1, H13, E3, E8 | — (anchor: fission→scan) |
| TSVC-2 | s1221 | tsvc.c:1049–1050 | `b[i] = b[i - 4] + a[i];` | C1: 4 independent chains; H13 yes; E3 (a scan per chain); E8 weak | R (≤4-way) / D beyond 4 threads | split by residue i mod 4 into 4 parallel chains (strided); with more threads, each chain becomes a scan | ok; no-init | IN C1/E1, H13 | s424 (residue split) |
| TSVC-2 | s222 | tsvc.c:1071–1074 | `a[i] += b[i]*c[i]; e[i] = e[i-1]*e[i-1]; a[i] -= b[i]*c[i];` | C1 (partial); H13 yes | R (partial) | distribute: the a statements become Do-All; the e recurrence stays serial (the closed form e0^(2^i) is not bit-exact), so speedup is Amdahl-bounded | init: TSVC leaves e inherited (s222 has no e init; s211's e=1/(i+1) gives e[0]=1), so e stays exactly 1. The packager's e[0]=0.75 squares to 0 within ~12 steps, so the output cannot see the e part | IN C1/E1 (partial), H13 | s211 (fission) |

## Loop interchange (%2.3)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s231 | tsvc.c:1094–1096 | `for i: for j: aa[j][i] = aa[j-1][i] + bb[j][i];` | A: outer i is Do-All as written (columns are independent); H13 no | A (outer) | pragma (interchange only for locality) | 2D | IN ctrl-A | — |
| TSVC-2 | s232 | tsvc.c:1118–1120 | `for j: for i≤j: aa[j][i] = aa[j][i-1]*aa[j][i-1] + bb[j][i];` | A: rows are independent; H13 no | A (outer, triangular) | pragma + schedule | 2D; init (squaring: TSVC's aa=1, bb=0 keeps the values at 1) | IN ctrl-A | s231 |
| TSVC-2 | s1232 | tsvc.c:1140–1142 | `aa[i][j] = bb[i][j] + cc[i][j];` (i≥j) | A; H13 no | A | pragma + schedule | 2D; no-init | IN ctrl-A | s231 |
| TSVC-2 | s233 | tsvc.c:1164–1169 | `for i: { for j: aa[j][i] = aa[j-1][i] + cc[j][i]; for j: bb[j][i] = bb[j][i-1] + cc[j][i]; }` | C1 conditional; H13 yes (outer); **E8 depth 1, partial** (after step 1 nest 1 is Do-All) | A(inner 2nd loop, 255-trip) / R | Step 1: distribute outer i over the two inner loops; nest 1 becomes an outer-i Do-All. Step 2: interchange nest 2 (j outer), giving an outer-j Do-All. Step 2 cannot come first: an imperfect nest with two inner loops cannot be interchanged, and nest 1's column recurrence forbids putting j outside. After step 1 alone, nest 2 still has only its fine inner Do-All | 2D | IN C1 (conditional), H13, E8 | — (anchor: distribution→interchange) |
| TSVC-2 | s2233 | tsvc.c:1189–1194 | `… for j: bb[i][j] = bb[i-1][j] + cc[i][j];` | like s233, but nest 2 is carried along i with j free; E8 weak (after step 1, nest 2's inner j is already a row-contiguous Do-All; interchange only makes it coarser) | A(inner) / R | distribute, then optionally interchange | 2D; no-init | IN C1 (conditional), H13, E8(weak) | s233 |
| TSVC-2 | s235 | tsvc.c:1215–1218 | `a[i] += b[i]*c[i]; for j: aa[j][i] = aa[j-1][i] + bb[j][i]*a[i];` | A: outer i Do-All (imperfect nest); H13 no | A (outer) | pragma | 2D; L2D-trip | IN ctrl-A | s231 |

## Node splitting (%2.4)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s241 | tsvc.c:1240–1242 | `a[i] = b[i]*c[i]*d[i]; b[i] = a[i]*a[i+1]*d[i];` | C1: anti-dep on a[i+1]; H13 yes | R | copy old a | pkg | IN C1/E1, H13 (packaged) | s121 |
| TSVC-2 | s242 | tsvc.c:1267–1268 | `a[i] = a[i - 1] + s1 + s2 + b[i] + c[i] + d[i];` | D by the recorded convention; it is a prefix sum; E3 (scan); H13 yes | D (scan form known) | three-phase scan or `omp scan` (reassociates) | pre(s1=1, s2=2: main :4017, common.c:183–184) | IN ctrl-D, E3(scan) | s3112 |
| TSVC-2 | s243 | tsvc.c:1289–1292 | `…; a[i] = b[i] + a[i+1]*d[i];` | C1; H13 yes | R | copy old a | pkg | IN C1/E1, H13 (packaged) | s241 |
| TSVC-2 | s244 | tsvc.c:1313–1316 | `…; a[i+1] = b[i] + a[i+1]*d[i];` | C1: every store but the last is dead; H13 yes | R | Do-All plus a peeled last element | pkg | IN C1/E1, H13 (packaged) | — (anchor: dead store) |
| TSVC-2 | s1244 | tsvc.c:1335–1337 | `a[i] = b[i]+c[i]*c[i]+b[i]*b[i]+c[i]; d[i] = a[i] + a[i+1];` | C1: anti-dep on a[i+1]; H13 yes | R | node splitting: copy old a (or run the d loop first with the inline expression) | ok; no-init | IN C1/E1, H13 | s241 |
| TSVC-2 | s2244 | tsvc.c:1356–1358 | `a[i+1] = b[i] + e[i]; a[i] = b[i] + c[i];` | C1: carried write-after-write; H13 yes | R | Do-All `a[i]=b[i]+c[i]`, then `a[N-1]=b[N-2]+e[N-2]` | ok; no-init | IN C1/E1, H13 | s244 |

## Scalar and array expansion (%2.5; s258 has no marker; s261 sits under %2.7)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s251 | tsvc.c:1380–1382 | `s = b[i] + c[i]*d[i]; a[i] = s * s;` | A; H13 yes (s is at function scope, :1378, so shared) | A | `private(s)` | ok | IN ctrl-A, H13 | — (anchor: private scalar) |
| TSVC-2 | s1251 | tsvc.c:1402–1405 | `s = b[i]+c[i]; b[i] = a[i]+d[i]; a[i] = s*e[i];` | A; H13 yes | A | `private(s)` | ok; no-init | IN ctrl-A, H13 | s251 |
| TSVC-2 | s2251 | tsvc.c:1425–1428 | `a[i] = s*e[i]; s = b[i]+c[i]; b[i] = a[i]+d[i];` | C1; H13 yes (s is declared in the repetition body, so shared); **E8 depth 1, strict** | R | Step 1: scalar expansion of s, `tmp[i]=b[i]+c[i]`, computed before b is overwritten. Step 2, exposed by step 1: distribute into loop A (`tmp[i]=b[i]+c[i]`, Do-All) and loop B (`a[i]=(i?tmp[i-1]:0)*e[i]; b[i]=a[i]+d[i]`, Do-All). The other order is equally dependent: substituting s by b[i-1]+c[i-1] (s252's fix) creates a new anti-dep on b[i-1], which then needs s241's copy. After step 1 alone, DiscoPoP still sees a carried dependence | ok; no-init | IN C1/E1, H13, E8 | — (anchor: expansion→fission) |
| TSVC-2 | s3251 | tsvc.c:1447–1450 | `a[i+1] = b[i]+c[i]; b[i] = c[i]*e[i]; d[i] = a[i]*e[i];` | C1: flow on a[i] from iteration i-1; H13 yes | R | distribute: {a[i+1]…; b[i]…}, then the d loop | ok; no-init | IN C1/E1, H13 | s1213 |
| TSVC-2 | s252 | tsvc.c:1473–1476 | `s = b[i]*c[i]; a[i] = s + t; t = s;` | C1; H13 yes | R | substitute t = b[i-1]*c[i-1] | pkg | IN C1/E1, H13 (packaged) | — |
| TSVC-2 | s253 | tsvc.c:1498–1502 | `if (a[i] > b[i]) { s = a[i]-b[i]*d[i]; c[i] += s; a[i] = s; }` | A; H13 yes (s shared) | A | `private(s)` | ok | IN ctrl-A, H13 | s251 |
| TSVC-2 | s254 | tsvc.c:1526–1528 | `a[i] = (b[i] + x) * .5; x = b[i];` | C1; H13 yes | R | x = b[i-1] (wrap-around) | pkg | IN C1/E1, H13 (packaged) | s252 |
| TSVC-2 | s255 | tsvc.c:1552–1555 | `a[i] = (b[i]+x+y)*.333; y = x; x = b[i];` | C1; H13 yes | R | two-level wrap-around | pkg | IN C1/E1, H13 (packaged) | s254 |
| TSVC-2 | s256 | tsvc.c:1576–1579 | `for i: for j: a[j] = 1. - a[j-1]; aa[j][i] = a[j] + bb[j][i]*d[j];` | C1; H13 yes (a is rewritten by every i) | R | hoist the i-invariant a recurrence out of the i loop (a[j] depends only on a[0] and j), then the aa nest is Do-All; or array-privatise a | 2D; L2D-trip (a, d) | IN C1/E1, H13 | — |
| TSVC-2 | s257 | tsvc.c:1601–1604 | `for i: for j: a[i] = aa[j][i] - a[i-1]; aa[j][i] = a[i] + bb[j][i];` | C1; H13 yes; **E8 depth 1, partial** (after step 1 alone the inner j loop becomes a fine Do-All) | R | Step 1: array expansion of a[i] over j. Its value per (i,j) is aa_old[j][i]−a[i−1], and the rewrites across j are dead; this removes the output and anti deps on a[i] inside j. Step 2, exposed by step 1: distribute into (i) a serial 255-step recurrence `a[i]=aa_old[LEN_2D-1][i]-a[i-1]`, run FIRST, and (ii) a Do-All nest `aa[j][i]=(aa[j][i]-a[i-1])+bb[j][i]`. Bit-exact. Before step 1, the write to a[i] in every j couples the nest | 2D; L2D-trip (a) | IN C1/E1, H13, E8 | — |
| TSVC-2 | s258 | tsvc.c:1626–1631 | `if (a[i] > 0.) s = d[i]*d[i]; b[i] = s*c[i]+d[i]; e[i] = (s+1.)*aa[0][i];` | **E2b**: a=1/(i+1)>0 in initialise_arrays (common.c:415, another function), and the loop never writes a. So s is set in every iteration and no value is carried. pkg→ init_array. H13 yes (s is shared, :1623). With generic data: E3 (segmented last-value scan) and E8 (chunk, carry scan, fix-up) | A (data-cond., private s) / R generic | shipped data: `private(s)`; generic data: three-phase last-value scan | L2D-trip (256 iterations over 1-D arrays; LEN_1D does not size it); 2D (aa row 0); init (a>0; the packager's default is also >0) | IN E2b, H13; E8 only with mixed-sign a (author) | — |
| TSVC-2 | s261 | tsvc.c:1653–1657 | `t = a[i]+b[i]; a[i] = t + c[i-1]; t = c[i]*d[i]; c[i] = t;` | C1: flow on c[i-1] from iteration i-1; H13 yes | R | distribute: the c loop first, then the a loop; t private | ok | IN C1/E1, H13 | s1213 |

## Control flow (%2.7)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s271 | tsvc.c:1676–1678 | `if (b[i] > 0.) a[i] += b[i]*c[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s000 |
| TSVC-2 | s272 | tsvc.c:1703–1706 | `if (e[i] >= t) { a[i] += c[i]*d[i]; b[i] += c[i]*c[i]; }` | A; H13 no | A | pragma | pre(t); pun: under float t=1065353216 and the branch never fires; under the packager's double t=0 and it always fires | IN ctrl-A | s271 |
| TSVC-2 | s273 | tsvc.c:1728–1732 | `a[i] += d[i]*e[i]; if (a[i] < 0.) b[i] += …; c[i] += a[i]*d[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s271 |
| TSVC-2 | s274 | tsvc.c:1753–1758 | `a[i] = c[i]+e[i]*d[i]; if (a[i] > 0.) b[i] = a[i]+b[i]; else a[i] = d[i]*e[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s271 |
| TSVC-2 | s275 | tsvc.c:1780–1783 | `if (aa[0][i] > 0.) for j: aa[j][i] = aa[j-1][i] + bb[j][i]*cc[j][i];` | A: outer i Do-All (column i; aa[0][i] is never written); H13 no | A (outer) | pragma | 2D | IN ctrl-A | s231 |
| TSVC-2 | s2275 | tsvc.c:1803–1807 | `for j: aa[j][i] = aa[j][i] + bb[j][i]*cc[j][i]; a[i] = b[i]+c[i]*d[i];` | A: outer i Do-All; H13 no | A (outer) | pragma | 2D; L2D-trip; no-init | IN ctrl-A | s231 |
| TSVC-2 | s276 | tsvc.c:1829–1833 | `if (i+1 < mid) a[i] += b[i]*c[i]; else a[i] += b[i]*d[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s271 |
| TSVC-2 | s277 | tsvc.c:1854–1863 | `if (a[i] >= 0.) goto L20; if (b[i] >= 0.) goto L30; a[i] += c[i]*d[i]; L30: b[i+1] = c[i]+d[i]*e[i];` | **E2b**: a=1 in initialise_arrays (common.c:458, another function), so the first test always jumps and the b[i+1]→b[i] dependence shown in the text never fires. pkg→ init_array. H13 no (data-cond.). With generic data (some a<0): C1 and **E8**. Step 1 forward-substitutes b[i] (= a_old[i-1]<0 ? c[i-1]+d[i-1]*e[i-1] : b_old[i]) and distributes. That creates a read of a[i-1]'s OLD value while iteration i-1 updates it, so step 2 copies a (node splitting) | A (data-cond., no-op) / R generic | shipped data: pragma; generic data: substitution + distribution + copy | init: with the shipped data (and with the packager's a>0) the loop does NO work; flag | IN E2b (no work: author); E8 only with mixed-sign a | — |
| TSVC-2 | s278 | tsvc.c:1886–1895 | `if (a[i] > 0.) goto L20; b[i] = -b[i]+…; goto L30; L20: c[i] = …; L30: a[i] = b[i]+c[i]*d[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s271 |
| TSVC-2 | s279 | tsvc.c:1916–1929 | nested if/goto on a[i] and b[i]; `a[i] = b[i]+c[i]*d[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s271 |
| TSVC-2 | s1279 | tsvc.c:1948–1951 | `if (a[i] < 0.) if (b[i] > a[i]) c[i] += d[i]*e[i];` | A; H13 no | A | pragma | ok; no-init | IN ctrl-A | s271 |
| TSVC-2 | s2710 | tsvc.c:1977–1991 | `if (a[i] > b[i]) {…} else { b[i] = …; if (x > 0.) c[i] = …; else c[i] += …; }` | A; H13 no | A | pragma | pre(x); pun (float gives x>0, double gives 0: this changes which branch runs, not the parallelism) | IN ctrl-A | s271 |
| TSVC-2 | s2711 | tsvc.c:2013–2015 | `if (b[i] != 0.0) a[i] += b[i]*c[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s271 |
| TSVC-2 | s2712 | tsvc.c:2037–2039 | `if (a[i] > b[i]) a[i] += b[i]*c[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s271 |

## Crossing thresholds (%2.8)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s281 | tsvc.c:2063–2066 | `x = a[LEN_1D-i-1] + b[i]*c[i]; a[i] = x-1.0; b[i] = x;` | C1: the second half reads the new first half; H13 yes | R | index-set split at N/2 | pkg | IN C1/E1, H13 (packaged) | — (anchor: index-set split) |
| TSVC-2 | s1281 | tsvc.c:2087–2090 | `x = b[i]*c[i] + a[i]*d[i] + e[i]; a[i] = x-1.0; b[i] = x;` | A; H13 yes (x shared) | A | `private(x)` | ok; no-init (its init key is misspelt as "1s281", common.c:497) | IN ctrl-A, H13 | s251 |

## Loop peeling (%2.9)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s291 | tsvc.c:2113–2115 | `a[i] = (b[i] + b[im1]) * .5; im1 = i;` | C1; H13 yes | R | im1 = i-1, peel i=0 | pkg | IN C1/E1, H13 (packaged) | s254 |
| TSVC-2 | s292 | tsvc.c:2140–2143 | `a[i] = (b[i]+b[im1]+b[im2])*.333; im2 = im1; im1 = i;` | C1; H13 yes | R | two-level peel | pkg | IN C1/E1, H13 (packaged) | s291 |
| TSVC-2 | s293 | tsvc.c:2164–2165 | `a[i] = a[0];` | C1: iteration 0 writes a[0], which every iteration reads; H13 yes (race, TSan) | R | a0 = a[0], then Do-All | pkg | IN C1/E1, H13 (packaged) | — (anchor: peel) |

## Diagonals and wavefronts (%2.10, %2.12, %2.11)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s2101 | tsvc.c:2187–2188 | `aa[i][i] += bb[i][i] * cc[i][i];` | A; H13 no | A | pragma | 2D (only LEN_2D elements of work) | IN ctrl-A | s000 |
| TSVC-2 | s2102 | tsvc.c:2209–2213 | `for j: aa[j][i] = 0.; aa[i][i] = 1.;` | A: outer i touches column i only; H13 no | A (outer) | pragma | 2D | IN ctrl-A | s231 |
| TSVC-2 | s2111 | tsvc.c:2233–2235 | `aa[j][i] = (aa[j][i-1] + aa[j-1][i]) / 1.9;` | C1; H13 yes; **E8 depth 1, strict** | R | Step 1: rectangular tiling. It is legal because the deps (0,1) and (1,0) are non-negative, so the nest is fully permutable. Step 2 works on the tile loops step 1 created: skew them into a wavefront over anti-diagonals of tiles, whose inner tile loop is Do-All. Skewing first and tiling second is equivalent. A plain skewed wavefront alone has about 2·LEN_2D barriers on diagonals of ≤LEN_2D elements. After step 1 alone, the tile loops still carry both deps. Bit-exact | 2D (LEN_2D must grow; 256² is tiny) | IN C1/E1, H13, E8 | — |

## Reductions (%3.1)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s311 | tsvc.c:2265–2266 | `sum += a[i];` | E3-ctrl (+); H13 yes | A | `reduction(+)` | ret: sum only reaches `dummy` (tsvc.c:2268); the packager returns 0, so at -O2 the loop is dead code | IN E3-ctrl | s313 |
| TSVC-2 | s31111 | tsvc.c:2293–2301 | `sum += test(a); … sum += test(&a[28]);` (8 calls, each summing 4 elements) | none: no loop over data, 32 elements | — | — | size fixed at 32 elements; ret; no-init | OUT: size not selectable (hard-coded a[0..31]); no loop region | — |
| TSVC-2 | s312 | tsvc.c:2323–2324 | `prod *= a[i];` | E3-ctrl (*); H13 yes | A | `reduction(*)` | init: TSVC's a=1.000001 (common.c:523); with the packager's 0.75–1.25 the product underflows at the larger sizes (STANDARD and up) | IN E3-ctrl | s313 |
| TSVC-2 | s313 | tsvc.c:2346–2347 | `dot += a[i] * b[i];` | E3-ctrl (+); H13 yes | A | `reduction(+)` | pkg | IN E3-ctrl (packaged) | — (anchor: + control) |
| TSVC-2 | s314 | tsvc.c:2370–2372 | `if (a[i] > x) x = a[i];` | E3 (max); H13 yes | R(clause) | `reduction(max:x)`, which is a clause, so not C1 | ok (returns x) | IN E3 | — (anchor: max) |
| TSVC-2 | s315 | tsvc.c:2401–2405 | `if (a[i] > x) { x = a[i]; index = i; }` | E3 (max with its first index); H13 yes | R(construct) | a user-defined (value, index) reduction, or per-thread partials combined keeping the smallest index on ties | ok (`a[i]=(i*7)%LEN_1D` sits after t1 at tsvc.c:2393–2394 and is copied; the values are distinct because gcd(7,N)=1 for every ladder size) | IN E3 | — (anchor: maxloc) |
| TSVC-2 | s316 | tsvc.c:2429–2431 | `if (a[i] < x) x = a[i];` | E3 (min); H13 yes | R(clause) | `reduction(min)` | ok | IN E3 | s314 |
| TSVC-2 | s317 | tsvc.c:2456–2457 | `q *= (real_t).99;` | E3-ctrl (*); reads no data | A | `reduction(*)` (closed form .99^(N/2)) | the kernel's own result (q) does not depend on the input; validate() (prepare_tsvc.py:811–812) will not flag this, because the a..e dumps still change with the seed | IN E3-ctrl (weak) | s312 |
| TSVC-2 | s318 | tsvc.c:2487–2494 | `if (ABS(a[k]) <= max) goto L5; index = i; max = ABS(a[k]); L5: k += inc;` | E3 (max-abs with index); k is an induction; H13 yes; E8 weak (the substitution k=inc·i does not create the reduction) | R | k=inc*i, then a (value, index) reduction | pre(inc from main :4064), ABS | IN E3 | s315 |
| TSVC-2 | s319 | tsvc.c:2518–2522 | `a[i] = c[i]+d[i]; sum += a[i]; b[i] = c[i]+e[i]; sum += b[i];` | E3-ctrl (+); H13 yes | A | `reduction(+)` | ok | IN E3-ctrl | s313 |
| TSVC-2 | s3110 | tsvc.c:2549–2555 | `if (aa[i][j] > max) { max = aa[i][j]; xindex = i; yindex = j; }` | E3 (max with two indices, first occurrence); H13 yes | R(construct) | a user-defined (value, i, j) reduction | 2D | IN E3 | s315 |
| TSVC-2 | s13110 | tsvc.c:2581–2587 | same as s3110 | E3; H13 yes | R(construct) | as s3110 | 2D; no-init | IN E3 | s3110 |
| TSVC-2 | s3111 | tsvc.c:2612–2614 | `if (a[i] > 0.) sum += a[i];` | E3-ctrl (+); H13 yes | A | `reduction(+)` | ok | IN E3-ctrl | s313 |
| TSVC-2 | s3112 | tsvc.c:2638–2640 | `sum += a[i]; b[i] = sum;` | D recorded; E3 (scan); E8 only in the hand-written form (chunk sums, then a scan of the sums, then fix-up; step 2 works on the chunk sums step 1 created); H13 yes | D (scan form known) | `omp scan` (a single construct; clang-20 support unverified) or three-phase; reassociates the additions | pkg | IN ctrl-D (packaged); E3; E8 only as the hand-written form | — (anchor: scan) |
| TSVC-2 | s3113 | tsvc.c:2663–2665 | `if ((ABS(a[i])) > max) max = ABS(a[i]);` | E3 (max); H13 yes | R(clause) | `reduction(max)` over fabs | ABS | IN E3 | s314 |

## Recurrences (%3.2)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s321 | tsvc.c:2687–2688 | `a[i] += a[i-1] * b[i];` | D recorded. A parallel form is known: an affine-map scan (E3: a user-defined scan; E8 in the hand form: chunk-local (mul, add) maps, a scan of the maps, then fix-up), at about 2× the work, with reassociated products; H13 yes | D | decline (as recorded) or the affine scan (the author decides) | pkg | IN ctrl-D (packaged) | — (anchor: recurrence) |
| TSVC-2 | s322 | tsvc.c:2709–2710 | `a[i] = a[i] + a[i-1]*b[i] + a[i-2]*c[i];` | D recorded; the scan form needs 2×2 matrix-affine maps (about 4× the work); H13 yes | D | decline | pkg | IN ctrl-D (packaged) | s321 |
| TSVC-2 | s323 | tsvc.c:2731–2733 | `a[i] = b[i-1] + c[i]*d[i]; b[i] = a[i] + c[i]*e[i];` | D recorded. But substituting a gives b[i] = b[i-1] + c·d + c·e, a plain prefix sum. So a strict E8 is possible: step 1 (forward substitution) exposes the scan, step 2 is the scan (arguably depth 2 when written by hand in three phases), then a[i] = b[i-1] + c·d is Do-All (reassociated); H13 yes | D recorded / R by the scan form | decline (as recorded) or substitution + scan (the author decides) | pkg | IN ctrl-D (packaged); E8 candidate if the author accepts the reassociation | s221 (scan form) |

## Search loops (%3.3)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s331 | tsvc.c:2757–2760 | `if (a[i] < 0.) j = i;` | E3 (last index = a max-index reduction); C1 (the body must be rewritten as `if (i>j) j=i`); H13 yes | R | `reduction(max:j)` after the rewrite | pkg | IN C1/E1, E3, H13 (packaged) | — (anchor: max index) |
| TSVC-2 | s332 | tsvc.c:2789–2794 | `if (a[i] > t) { index = i; value = a[i]; goto L20; }` | E3 (find-first: min-index or cancel); H13 compile error (goto out of an omp for); E2b weak: t is read through `int*` from `&s1` (tsvc.c:2778; main :4075; s1=1.0 at common.c:183). Under float t=1065353216, so nothing is found and the loop scans everything. Under double t=0, so it exits at i=0 | R(construct) | a min-index reduction over {i : a[i]>t}, then value = a[idx] | pre(t); pun: the author must choose t; ret (value + index; the shipped return drops index) | IN E3; E2b(weak) | s331 |

## Packing (%3.4)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s341 | tsvc.c:2820–2823 | `if (b[i] > 0.) { j++; a[j] = b[i]; }` | C1; H13 yes; E3 (scan); **E8 strict, arguably depth 2** (three dependent phases): step 1 splits into per-thread chunks with a count per chunk; step 2 is an exclusive scan of the chunk counts step 1 created; then the scatter at the resulting offsets | R | count, exclusive scan of the counts, scatter (reference exists) | pkg | IN C1/E1, H13, E3, E8 (packaged) | — (anchor: pack) |
| TSVC-2 | s342 | tsvc.c:2848–2851 | `if (a[i] > 0.) { j++; a[i] = b[j]; }` | C1; H13 yes; E8 (as s341); E2b weak: a=1/(i+1)>0 (common.c:577) and b>0 keep every a[i]>0, so j=i | R | count, scan, gather | ok (the packager's a>0 also degenerates to j=i; the generic path needs a sign mix in init) | IN C1/E1, H13, E8 | s341 |
| TSVC-2 | s343 | tsvc.c:2876–2880 | `if (bb[j][i] > 0.) { k++; flat_2d_array[k] = aa[j][i]; }` | C1; H13 yes; E8 (as s341); E2b weak: bb=1 (common.c:581), so k = i·LEN_2D+j | R | count, scan, scatter | 2D, flat | IN C1/E1, H13, E8 | s341 |

## Loop rerolling (%3.5)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s351 | tsvc.c:2904–2909 | `a[i] += alpha*b[i]; … a[i+4] += alpha*b[i+4];` (i+=5) | A; H13 no | A | pragma | ok (alpha = c[0] is set after t1 and copied) | IN ctrl-A | s000 |
| TSVC-2 | s1351 | tsvc.c:2927–2934 | `*A = *B + *C; A++; B++; C++;` | C1: pointer inductions are carried; H13 yes | R | index form A[i] = B[i] + C[i] | ok; no-init | IN C1/E1, H13 | s127 |
| TSVC-2 | s352 | tsvc.c:2957–2959 | `dot = dot + a[i]*b[i] + … + a[i+4]*b[i+4];` | E3-ctrl (+); H13 yes | A | `reduction(+)` | ok | IN E3-ctrl | s313 |
| TSVC-2 | s353 | tsvc.c:2985–2990 | `a[i] += alpha * b[ip[i]]; …` (i+=5) | A: gather only; H13 no | A | pragma | pkg (ip) | IN ctrl-A (packaged) | s4112 |

## Storage classes and equivalencing (%4.1 has no loop; %4.2)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s421 | tsvc.c:3020–3022 | `yy = xx; for: xx[i] = yy[i+1] + a[i];` | C1; H13 yes; E2a weak: yy aliases xx (`yy = xx` one line above the loop; `xx = flat_2d_array` at :3017; same function), so the different names hide an anti-dep | R | copy old values | flat; xx (drop `__restrict__`: xx is declared restrict at tsvc.c:44, and writing through xx while reading the same storage through yy is undefined behaviour, so clang may reorder and the oracle becomes a determinism risk); ret (the checksum is sum_xx) | IN C1/E1, H13, E2a(weak) | s121 (fix); s422 (property) |
| TSVC-2 | s1421 | tsvc.c:3043–3044 | `b[i] = xx[i] + a[i];` (i<N/2) | A; E2b weak: `xx = &b[LEN_1D/2]` (tsvc.c:3040, one line above, same function) puts the reads in b's upper half and the writes in its lower half; H13 no (data-cond.) | A | pragma | xx (restrict holds here: the elements are disjoint) | IN ctrl-A, E2b(weak) | s431 |
| TSVC-2 | s422 | tsvc.c:3068–3069 | `xx[i] = flat_2d_array[i + 8] + a[i];` | C1; H13 yes; E2a weak: `xx = flat_2d_array + 4` (tsvc.c:3065, same function), so the loop writes flat[i+4] and reads flat[i+8]: anti-dep at distance 4 | R | copy | flat; xx (drop restrict); ret (sum_xx); init (flat is zero, common.c:620–622) | IN C1/E1, H13, E2a(weak) | s421 |
| TSVC-2 | s423 | tsvc.c:3094–3095 | `flat_2d_array[i+1] = xx[i] + a[i];` | C1; H13 yes; E2a weak: `vl = 64; xx = flat_2d_array + vl` (tsvc.c:3087–3088, same function, BEFORE the timer) gives an anti-dep at distance 63; pkg→ pre (the kernel's first lines, the same function as shipped) | R | copy | pre(vl, xx); flat; xx (drop restrict) | IN C1/E1, H13, E2a(weak) | s421 |
| TSVC-2 | s424 | tsvc.c:3121–3122 | `xx[i+1] = flat_2d_array[i] + a[i];` | C1; H13 yes; E2a weak: `vl = 63; xx = flat_2d_array + vl` (tsvc.c:3114–3115, before the timer) gives a TRUE dep at distance 64 that the alias hides, i.e. 64 independent chains | R | residue split: 64 chains i≡r (mod 64) run in parallel, each one serial (strided); bit-exact | pre(vl, xx); flat; xx (drop restrict); ret (sum_xx) | IN C1/E1, H13, E2a(weak) | — (anchor: residue split) |

## Parameters (%4.3)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s431 | tsvc.c:3147–3148 | `a[i] = a[i+k] + b[i];` | A; E2b weak: `k = 2*k1-k2 = 0` (tsvc.c:3139–3141, same function, before the timer), so there is no dependence although the text reads like s131; pkg→ pre (same function); H13 no (data-cond.) | A | pragma | pre(k1, k2, k) | IN ctrl-A, E2b(weak) | — (anchor: E2b from a constant in the same function) |

## Non-logical ifs (%4.4)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s441 | tsvc.c:3169–3175 | `if (d[i] < 0.) a[i] += …; else if (d[i] == 0.) …; else …;` | A; H13 no | A | pragma | ok | IN ctrl-A | s271 |
| TSVC-2 | s442 | tsvc.c:3197–3214 | `switch (indx[i]) { case 1: goto L15; … }` then `a[i] += …` | A: indx (init() common.c:179–181) only selects a branch, and every branch writes a[i]; H13 no | A | pragma | indx | IN ctrl-A | s271 |
| TSVC-2 | s443 | tsvc.c:3237–3247 | `if (d[i] <= 0.) goto L20; else goto L30; L20: a[i] += b[i]*c[i]; …` | A; H13 no | A | pragma | ok | IN ctrl-A | s271 |

## Intrinsic functions (%4.5)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s451 | tsvc.c:3270–3271 | `a[i] = sinf(b[i]) + cosf(c[i]);` | A; H13 no | A | pragma | ok (float intrinsics on double data) | IN ctrl-A | s000 |
| TSVC-2 | s452 | tsvc.c:3292–3293 | `a[i] = b[i] + c[i] * (real_t) (i+1);` | A; H13 no | A | pragma | ok | IN ctrl-A | s000 |
| TSVC-2 | s453 | tsvc.c:3316–3318 | `s += (real_t)2.; a[i] = s * b[i];` | C1: s is carried; H13 yes | R | s = 2*(i+1) (exact in double) | ok | IN C1/E1, H13 | s127 |

## Call statements (%4.7)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s471 | tsvc.c:3345–3348 | `x[i] = b[i] + d[i]*d[i]; s471s(); b[i] = c[i] + d[i]*e[i];` | A; **E2b**: whether the call has side effects is decided in another function (`s471s`, tsvc.c:3329–3333, empty); pkg→ fn; H13 no | A | pragma | x; fn(s471s); pre(m = LEN_1D, tsvc.c:3339); regex: the one-line signature `…func_args){` at tsvc.c:3335 does not match `_tsvc_function`'s `\n{\n` (prepare_tsvc.py:569) | IN ctrl-A, E2b | s4121 |

## Non-local gotos (%4.8, twice)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s481 | tsvc.c:3369–3373 | `if (d[i] < 0.) exit (0); a[i] += b[i] * c[i];` | E3 (early exit); E2b: d=1/(i+1)>0 (common.c:677), so exit never fires; pkg→ init_array; H13 no (data-cond.; exit() is legal inside an omp for) | A (data-cond.) | shipped data: pragma; generic data: test any(d<0) first, then Do-All | init (the packager's d is also >0) | IN E3(weak), E2b | — |
| TSVC-2 | s482 | tsvc.c:3395–3397 | `a[i] += b[i] * c[i]; if (c[i] > b[i]) break;` | E3 (early exit → min-index); H13 compile error (break inside an omp for); E8 weak; E2b: b and c are both 1/(i+1) (common.c:680–681), so c>b never holds and the shipped data never exits | R | Step 1: distribute the exit test from the update. This is legal because the test reads b and c and the update writes a. It gives a search loop and an update over [0, k]. Step 2 works on the exposed search loop: find-first becomes `reduction(min:k)`. It is weak because after step 1 the bounded update is already Do-All | init: the packager's default init breaks at i=1 (c[1]=0.7855 > b[1]=0.7765, prepare_tsvc.py:477–478), so the loop has no work. Copy TSVC's b=c or choose a late exit | IN E3, H13 (compile error), E2b; E8(weak) | — |

## Vector semantics (%4.9)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s491 | tsvc.c:3422–3423 | `a[ip[i]] = b[i] + c[i] * d[i];` | A (data-cond.); **E2b**: ip is a permutation (each block of 5 maps onto {i..i+4}; init() common.c:161–167, another file, passed from main :4098), so no two iterations write the same element; pkg→ the `pb_ip` values in init_array (another function); H13 no (data-cond.) | A | pragma | pkg (ip) | IN ctrl-A, E2b (packaged) | — (anchor: scatter through a permutation) |

## Indirect addressing (%4.11)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s4112 | tsvc.c:3450–3451 | `a[i] += b[ip[i]] * s;` | A: gather only, and the independence is visible; H13 no | A | pragma | pkg (ip; pre s=1.0) | IN ctrl-A (packaged) | — (anchor: gather) |
| TSVC-2 | s4113 | tsvc.c:3476–3477 | `a[ip[i]] = b[ip[i]] + c[i];` | A (data-cond.); E2b: ip is a permutation, as in s491; H13 no (data-cond.) | A | pragma | pkg (ip) | IN ctrl-A, E2b (packaged) | s491 |
| TSVC-2 | s4114 | tsvc.c:3505–3508 | `k = ip[i]; a[i] = b[i] + c[LEN_1D-k+1-2] * d[i]; k += 5;` | A (private k); H13 yes (k is declared before the repetition loop, so shared) | A | `private(k)` | pkg (ip; pre n1=1) | IN ctrl-A, H13 (packaged) | s251 |
| TSVC-2 | s4115 | tsvc.c:3535–3536 | `sum += a[i] * b[ip[i]];` | E3-ctrl (+); H13 yes | A | `reduction(+)` | pkg (ip) | IN E3-ctrl (packaged) | s313 |
| TSVC-2 | s4116 | tsvc.c:3567–3569 | `off = inc + i; sum += a[off] * aa[j-1][ip[i]];` | E3-ctrl (+); H13 yes (sum and off shared) | A | `reduction(+)`, `private(off)` | 2D (row j-1 = LEN_2D/2-1); ip; pre(j = LEN_2D/2, inc = 1, main :4103); LEN_2D-1 trips | IN E3-ctrl | s4115 |
| TSVC-2 | s4117 | tsvc.c:3590–3591 | `a[i] = b[i] + c[i/2] * d[i];` | A; H13 no | A | pragma | pkg | IN ctrl-A (packaged) | s4112 |

## Statement functions (%4.12)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | s4121 | tsvc.c:3616–3617 | `a[i] += f(b[i],c[i]);` | A; **E2b**: that f is pure is decided in another function (tsvc.c:3602–3604); pkg→ f stays a separate function in the file (prepare_tsvc.py:389); H13 no | A | pragma | pkg | IN ctrl-A, E2b (packaged) | — (anchor: pure callee) |

## Control loops (%5.1)

| source | name | where | hot loop | properties HAS | pred. class | expert / parallel form | constraints & packaging | verdict | dup-of |
|---|---|---|---|---|---|---|---|---|---|
| TSVC-2 | va | tsvc.c:3638–3639 | `a[i] = b[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s000 |
| TSVC-2 | vag | tsvc.c:3664–3665 | `a[i] = b[ip[i]];` | A: gather; H13 no | A | pragma | ip; pre (bind ip as the probes do) | IN ctrl-A | s4112 |
| TSVC-2 | vas | tsvc.c:3690–3691 | `a[ip[i]] = b[i];` | A (data-cond.); E2b: ip is a permutation (as in s491); H13 no (data-cond.) | A | pragma | ip | IN ctrl-A, E2b | s491 |
| TSVC-2 | vif | tsvc.c:3712–3714 | `if (b[i] > 0.) a[i] = b[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s271 |
| TSVC-2 | vpv | tsvc.c:3736–3737 | `a[i] += b[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s000 |
| TSVC-2 | vtv | tsvc.c:3758–3759 | `a[i] *= b[i];` | A; H13 no | A | pragma | ok (init: products repeat; TSVC's b=1) | IN ctrl-A | s000 |
| TSVC-2 | vpvtv | tsvc.c:3780–3781 | `a[i] += b[i] * c[i];` | A; H13 no | A | pragma | pkg | IN ctrl-A (packaged) | s000 |
| TSVC-2 | vpvts | tsvc.c:3805–3806 | `a[i] += b[i] * s;` | A; H13 no | A | pragma | pre(s); pun (float gives s=1.07e9; double gives s=0, which leaves a unchanged, so the output does not depend on the loop) | IN ctrl-A | s000 |
| TSVC-2 | vpvpv | tsvc.c:3827–3828 | `a[i] += b[i] + c[i];` | A; H13 no | A | pragma | ok | IN ctrl-A | s000 |
| TSVC-2 | vtvtv | tsvc.c:3849–3850 | `a[i] = a[i] * b[i] * c[i];` | A; H13 no | A | pragma | ok (init: TSVC's b=2, c=.5 keeps a at 1) | IN ctrl-A | s000 |
| TSVC-2 | vsumr | tsvc.c:3873–3874 | `sum += a[i];` | E3-ctrl (+); H13 yes | A | `reduction(+)` | ok (returns sum) | IN E3-ctrl | s313 |
| TSVC-2 | vdotr | tsvc.c:3897–3898 | `dot += a[i] * b[i];` | E3-ctrl (+); H13 yes | A | `reduction(+)` | ok | IN E3-ctrl | s313 |
| TSVC-2 | vbor | tsvc.c:3921–3935 | `a1 = a[i]; … f1 = aa[0][i]; … x[i] = a1 * b1 * c1 * d1;` | A; H13 yes (a1..f1 are at function scope, :3919, so shared) | A | `private(a1..f1)` | L2D-trip; 2D (aa row 0); x (the checksum is sum_x) | IN ctrl-A, H13 | s251 |

## Summary

**C1 / E1 (predicted class R, and the expert form restructures)**
- Already packaged (18): s112, s121, s127, s211, s212, s1213, s241, s243, s244, s252, s254, s255, s281, s291, s292, s293, s331, s341.
- New candidates (33): s1113, s116, s122, s123, s124, s125, s126, s128, s131, s151, s161, s162, s175, s221, s1221, s222 (partial), s1244, s2244, s2251, s3251, s256, s257, s261, s2111, s342, s343, s1351, s421, s422, s423, s424, s453, s482.
- Conditional on T0.11, because only a fine inner Do-All exists as written: s233, s2233, s1119, s176.
- Only with generic data, because the shipped data makes them no-ops or data-conditional: s277, s258.

**H13**
- Yes for every C1 row.
- Yes for every reduction row: s311, s312, s313, s314, s315, s316, s317, s318, s319, s3110, s13110, s3111, s3112, s3113, s352, s4115, s4116, vsumr, vdotr.
- Yes for the recurrences: s118, s242, s321, s322, s323.
- Yes for the class-A rows with a shared scalar: s141, s251, s1251, s253, s1281, s4114, vbor, s258.
- A compile error for s332 and s482.
- "No (data-cond.)" for s132, s171, s173, s277, s431, s481, s491, s4113, vas, s1421.

**E2-B1, with where the deciding fact sits as shipped**
- (a) Hidden dependence:
  - In another function or file: s161 (b's sign pattern over b[0..N/2), common.c:296–297; the packager's default init loses it) and s151 (the distance is passed by the caller, tsvc.c:674).
  - In the same function: s131 (one line above), s421 (an alias one line above), s422 (one line above), s423 and s424 (above the timer; `pre` keeps them in the same function).
- (b) Hidden independence:
  - In another function or file: s171 (inc comes from main; needs glob, not pre); s491, s4113 and vas (ip is a permutation, common.c:161–167); s152, s471 and s4121 (the callee decides); s258, s277, s481 and s482 (the initial values decide); s123, s342 and s343 (the initial values turn a data-dependent index into a fixed stride; weak).
  - In the same function: s132, s173, s431, s1421.
  - Through the type-pun, so it depends on float vs double: s332.
- Strongest cases: s161 and s151 for (a); s171, s491 and s4113 for (b).
- In TSVC no fact is set in the harness itself. It sits in `main`/`init()`, which the packager turns into `init_array` (another function) or `pre` (same function).

**E3 (needs a construct DiscoPoP cannot generate)**
- min or max: s314, s316, s3113.
- max or min with an index: s315, s318, s331 (pkg), s3110, s13110.
- early exit: s332, s481, s482.
- scan: s3112 (pkg), s242, s221 (after fission), s1221, s323 (after substitution), s341 (pkg), s342, s343, s123.
- scan over affine maps: s321 and s322 (recorded as D).
- array reduction, as an optional alternative form: s176.
- In-pattern `+`/`*` controls: s311, s312, s313 (pkg), s317, s319, s3111, s352, s4115 (pkg), s4116, vsumr, vdotr.
- **No TSVC loop needs atomics, critical, tasks or cancel with the shipped data.** With TSVC's ip values, the scatters (s491, s4113, vas) are permutations. The only task-shaped code, s31111, is OUT.

**E8.** The ordered steps are in each row. "Strict" and "partial" are defined in the legend.
- Strict:
  - s2251: scalar expansion, then distribution (or substitution, then a copy).
  - s2111: tiling, then a wavefront skew of the tile loops.
  - s341 (pkg), and its duplicates s342, s343 and s123: count per chunk, then a scan of the counts, then the scatter.
  - s323: forward substitution exposes a prefix sum, then the scan (recorded as D; the author decides).
- Partial:
  - s221: fission, then a scan of the isolated b-loop.
  - s233: distribution, then interchange of nest 2.
  - s257: array expansion of a[i] over j, then distribution into a serial recurrence plus a Do-All nest.
- Data-conditional (only with generic data): s277 (forward substitution, then a copy of a) and s258 (chunking, then a last-value carry scan).
- Weak: s482, s2233, s318, s1221.
- As the hand form of a loop recorded as D (the author decides whether to relabel): s3112 and s321 (a chunk-local scan or affine maps, then a scan of the chunk totals, then fix-up).
- **Depth 2 (three dependent steps) is arguable.** It applies to the three-phase forms, where each phase acts on what the previous one created:
  - the s341 family: count, then a scan of the counts, then the scatter at the offsets step 2 created;
  - the hand-written scans (s3112, s221's b-loop, s323, s321): a local scan, then a scan of the chunk totals, then a fix-up add.

  Whether a three-phase scan is three restructuring steps or one idiom is the author's decision. No other TSVC loop needs three dependent steps.

**E9: none.** Each TSVC function is one kernel. Treating the whole tsvc.c as "a program" fails the constraints and the intent: it spans three files (tsvc.c, common.c, dummy.c; DiscoPoP defect B8), holds 151 unrelated kernels, and runs for hours at `iterations = 100000` (common.h).

**Controls**
- Class A: the rows marked ctrl-A. Anchors are s000, s231 (outer 2-D), s251 (private scalar), s4112 (gather), s491 (scatter) and s4121.
- Class D: s321, s322, s323 and s3112 (all packaged), plus s242, s118 and s115.

**OUT**: only s31111 (size fixed at 32 elements, and no loop region). Nothing else fails a hard constraint.

**Flags for the author (not exclusions)**
- No measurable work with the shipped data: s277; s272 (float); vpvts (double); s332 (double); s482 (with the packager's init).
- The kernel's result does not depend on the input: s317.
- Undefined behaviour under `restrict`: s421–s424.

**Packager extensions, ranked by how many candidates each unblocks**
1. **2-D arrays** (aa/bb/cc, a LEN_2D ladder, digest) unblock 29 rows: s114, s115, s1115, s118, s119, s1119, s125, s126, s132, s141, s231, s232, s1232, s233, s2233, s235, s256, s257, s258, s275, s2275, s2101, s2102, s2111, s3110, s13110, s343, s4116, vbor. That includes the E8 candidates s233, s257 and s2111, and the E3 candidates s3110 and s13110. s125, s126, s141 and s343 also need flat.
2. **init_extra** reproducing TSVC's data: s161 (E2a), s482, s312, s258, s277, s123, s342, s222.
3. **glob(v)** instead of `pre` for values that decide a dependence: s171, and s151 if its callee is inlined.
4. **flat + xx**, with `restrict` dropped: s421, s422, s423, s424 (E2a), s1421; s125, s126, s141 and s343 need flat as well.
5. **ret**: s311, s332, s421, s422, s424.
6. **fn**: s151, s152, s471.
7. **x**: s471, vbor.
8. **ABS**: s318, s3113.
9. **regex fix**: s471.
10. **pun decisions**: s272, s2710, s332, vpvts.

**Duplicates (same property, same fix)**
- Copy (anchor s121): s112, s116, s131, s151, s162, s175, s241, s243, s1244, s421, s422, s423.
- Induction substitution (anchor s127): s122, s124, s125, s126, s128, s453, s1351.
- Distribution (anchor s1213): s161, s212, s261, s3251.
- Pack (anchor s341): s123, s342, s343.
- Max or min with an index (anchor s315): s318, s3110, s13110.
- Private scalar (anchor s251): s141, s253, s1251, s1281, s4114, vbor.
- Scan (anchor s3112): s242, s1221, s323.
- Residue split (anchor s424): s1221.

A copy of this document is at `/private/tmp/claude-501/-Users-ahmedsamir-discopop-agent/e85577da-fd5c-4f2f-8fbd-0a36a7611b27/scratchpad/tsvc_screen.md`.