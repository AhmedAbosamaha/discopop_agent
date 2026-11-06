# E11 part 1 — NPB EP and CG: the registered read-out

Descriptive (one program per comparison system, five trials per setup). Usable = the harness's FASTER, clean in the race check, NPB's verification SUCCESSFUL at the second class (EP class B, CG class A).

## EP

### (1)–(2) Usable programs and speedups

| setup | trials | FASTER | race-clean | NPB second class OK | **usable** | speedup 6 thr, usable: median (range) | 12 thr | best |
|---|---|---|---|---|---|---|---|---|
| DiscoPoP alone | 5 | 0 | 5 | 5 | **0** | — | — | — |
| the agent | 5 | 5 | 5 | 5 | **5** | 5.12 (1.36–5.17) | 6.84 (1.14–7.80) | 7.80 |
| Sonnet 4.5 alone | 5 | 5 | 5 | 5 | **5** | 5.14 (5.11–5.56) | 8.59 (7.85–9.14) | 9.14 |
| RepoOMP's published Claude program (repoomp_published) | 1 | 1 | 1 | 1 | **1** | 5.87 | 8.61 | 8.61 |
| RepoOMP's Claude Code program | 1 | 0 | 0 | 0 | **0** | — | — | — |
| NPB's OpenMP version | 1 | 0 | 0 | 1 | **0** | 5.16 | 8.68 | 8.68 |

NPB's OpenMP EP: harness outcome BROKEN (values outside 1e-9; it prints NPB's full report, so the output comparison does not apply), NPB's verification at the second class SUCCESSFUL, measured speedup 5.16 / 8.68 at 6 / 12 threads; race check: ThreadSanitizer clean, its verdict `correctness` the first stage that failed (the race check's last stages compare the output with the package's sequential program, as the harness does).

Race check, every program not clean (verdict = the first stage that failed; ThreadSanitizer's own result beside it):

- RepoOMP's Claude Code program rep1: `compile`, ThreadSanitizer not run
- NPB's OpenMP version rep1: `correctness`, ThreadSanitizer clean

### (3) The headline

The agent reached a usable program in 5 of 5 trials; RepoOMP's published program is usable (one program, possibly its best of several). Speedup at 6 / 12 threads — the agent's usable trials: median 5.12 (1.36–5.17) / 6.84 (1.14–7.80), best 7.80; RepoOMP's: 5.87 / 8.61.

### (4) Calls, cost, BROKEN by cause

| setup | trials | calls | failed calls | cost (USD) | per trial | BROKEN: not repeatable | values outside 1e-9 | does not build |
|---|---|---|---|---|---|---|---|---|
| DiscoPoP alone | 5 | 0 | 0 | 0.00 | 0.00 | 0 | 0 | 0 |
| the agent | 5 | 22 | 0 | 8.24 | 1.65 | 0 | 0 | 0 |
| Sonnet 4.5 alone | 5 | 5 | 0 | 1.70 | 0.34 | 0 | 0 | 0 |

### Every trial

| setup | rep | outcome | race check | NPB 2nd class | usable | 6 / 12 thr | BROKEN cause | calls | cost |
|---|---|---|---|---|---|---|---|---|---|
| DiscoPoP alone | 1 | parallel-not-faster | clean | SUCCESSFUL | no | 1.00 / 1.00 | — | 0 | 0.00 |
| DiscoPoP alone | 2 | parallel-not-faster | clean | SUCCESSFUL | no | 1.00 / 1.00 | — | 0 | 0.00 |
| DiscoPoP alone | 3 | parallel-not-faster | clean | SUCCESSFUL | no | 1.00 / 1.00 | — | 0 | 0.00 |
| DiscoPoP alone | 4 | parallel-not-faster | clean | SUCCESSFUL | no | 1.00 / 0.95 | — | 0 | 0.00 |
| DiscoPoP alone | 5 | parallel-not-faster | clean | SUCCESSFUL | no | 1.00 / 1.00 | — | 0 | 0.00 |
| the agent | 1 | FASTER | clean | SUCCESSFUL | yes | 5.17 / 6.51 | — | 4 | 1.39 |
| the agent | 2 | FASTER | clean | SUCCESSFUL | yes | 1.36 / 1.14 | — | 6 | 2.66 |
| the agent | 3 | FASTER | clean | SUCCESSFUL | yes | 5.15 / 6.84 | — | 4 | 1.84 |
| the agent | 4 | FASTER | clean | SUCCESSFUL | yes | 5.12 / 7.80 | — | 4 | 1.19 |
| the agent | 5 | FASTER | clean | SUCCESSFUL | yes | 5.09 / 7.80 | — | 4 | 1.16 |
| Sonnet 4.5 alone | 1 | FASTER | clean | SUCCESSFUL | yes | 5.13 / 9.14 | — | 1 | 0.40 |
| Sonnet 4.5 alone | 2 | FASTER | clean | SUCCESSFUL | yes | 5.11 / 8.88 | — | 1 | 0.37 |
| Sonnet 4.5 alone | 3 | FASTER | clean | SUCCESSFUL | yes | 5.14 / 8.59 | — | 1 | 0.39 |
| Sonnet 4.5 alone | 4 | FASTER | clean | SUCCESSFUL | yes | 5.53 / 8.39 | — | 1 | 0.24 |
| Sonnet 4.5 alone | 5 | FASTER | clean | SUCCESSFUL | yes | 5.56 / 7.85 | — | 1 | 0.31 |
| RepoOMP's published Claude program (repoomp_published) | 1 | FASTER | clean | SUCCESSFUL | yes | 5.87 / 8.61 | — | 0 | 0.00 |
| RepoOMP's Claude Code program | 1 | SCAFFOLD_MODIFIED | compile | does-not-build | no | — / — | does not build | 0 | 0.00 |
| NPB's OpenMP version | 1 | BROKEN | correctness | SUCCESSFUL | no | 5.16 / 8.68 | values outside 1e-9 | 0 | 0.00 |

### (5) The directives of each usable program

- the agent rep1 (DiscoPoP 0, model 4):
    - `14: #pragma omp threadprivate(x)  →  static double q[NQ];`
    - `76: #pragma omp parallel private(t1, t2, t3, t4, x1, x2, kk, i, ik, l) reduction(+:sx,sy)  →  {`
    - `81: #pragma omp single  →  nthreads = omp_get_num_threads();`
    - `84: #pragma omp for  →  for (k = 1; k <= np; k++) {`
    - `126: #pragma omp critical  →  {`
- the agent rep2 (DiscoPoP 0, model 4):
    - `14: #pragma omp threadprivate(x)  →  static double q[NQ];`
    - `79: #pragma omp parallel private(kk,i,ik,t1,t2,t3,t4,x1,x2,l)  →  {`
    - `81: #pragma omp single  →  nthreads = omp_get_num_threads();`
    - `84: #pragma omp for reduction(+:sx,sy)  →  for (k = 1; k <= np; k++) {`
    - `118: #pragma omp atomic  →  qq[l] += 1.0;`
- the agent rep3 (DiscoPoP 0, model 4):
    - `14: #pragma omp threadprivate(x)  →  static double q[NQ];`
    - `73: #pragma omp parallel  →  {`
    - `81: #pragma omp for reduction(+:sx,sy)  →  for (k = 1; k <= np; k++) {`
    - `123: #pragma omp critical  →  {`
    - `128: #pragma omp single  →  {`
- the agent rep4 (DiscoPoP 0, model 3):
    - `14: #pragma omp threadprivate(x)  →  static double q[NQ];`
    - `79: #pragma omp parallel private(kk,t1,t2,t3,t4,x1,x2,ik,l,i) reduction(+:sx,sy,qq[:NQ])  →  {`
    - `81: #pragma omp single  →  nthreads = omp_get_num_threads();`
    - `84: #pragma omp for  →  for (k = 1; k <= np; k++) {`
- the agent rep5 (DiscoPoP 0, model 3):
    - `14: #pragma omp threadprivate(x)  →  static double q[NQ];`
    - `79: #pragma omp parallel private(kk, i, ik, l, t1, t2, t3, t4, x1, x2) reduction(+:sx,sy,qq[:NQ])  →  {`
    - `81: #pragma omp for  →  for (k = 1; k <= np; k++) {`
    - `123: #pragma omp master  →  nthreads = omp_get_num_threads();`
- Sonnet 4.5 alone rep1:
    - `14: #pragma omp threadprivate(x)  →  static double q[NQ];`
    - `72: #pragma omp parallel  →  {`
    - `80: #pragma omp for reduction(+:sx,sy)  →  for (k = 1; k <= np; k++) {`
    - `121: #pragma omp critical  →  {`
    - `125: #pragma omp single  →  {`
- Sonnet 4.5 alone rep2:
    - `14: #pragma omp threadprivate(x)  →  static double q[NQ];`
    - `79: #pragma omp parallel reduction(+:sx,sy) reduction(+:qq[0:NQ]) private(kk,i,ik,l,t1,t2,t3,t4,x1,x2)  →  {`
    - `81: #pragma omp for  →  for (k = 1; k <= np; k++) {`
    - `123: #pragma omp master  →  {`
- Sonnet 4.5 alone rep3:
    - `14: #pragma omp threadprivate(x)  →  static double q[NQ];`
    - `72: #pragma omp parallel copyin(x)  →  {`
    - `80: #pragma omp for reduction(+:sx,sy)  →  for (k = 1; k <= np; k++) {`
    - `121: #pragma omp critical  →  {`
    - `125: #pragma omp master  →  {`
- Sonnet 4.5 alone rep4:
    - `14: #pragma omp threadprivate(x)  →  static double q[NQ];`
    - `72: #pragma omp parallel  →  {`
    - `80: #pragma omp for reduction(+:sx,sy)  →  for (k = 1; k <= np; k++) {`
    - `121: #pragma omp critical  →  {`
    - `125: #pragma omp single  →  {`
- Sonnet 4.5 alone rep5:
    - `14: #pragma omp threadprivate(x)  →  static double q[NQ];`
    - `72: #pragma omp parallel  →  {`
    - `80: #pragma omp for reduction(+:sx,sy)  →  for (k = 1; k <= np; k++) {`
    - `121: #pragma omp critical  →  {`
    - `125: #pragma omp single  →  {`
- RepoOMP's published Claude program (repoomp_published) rep1:
    - `47: #pragma omp parallel  →  {`
    - `60: #pragma omp for schedule(static)  →  for (k = 1; k <= np; k++) {`
    - `92: #pragma omp critical  →  {`

## CG

### (1)–(2) Usable programs and speedups

| setup | trials | FASTER | race-clean | NPB second class OK | **usable** | speedup 6 thr, usable: median (range) | 12 thr | best |
|---|---|---|---|---|---|---|---|---|
| DiscoPoP alone | 5 | 5 | 5 | 5 | **5** | 5.70 (5.24–5.80) | 9.96 (8.48–10.14) | 10.14 |
| the agent | 5 | 5 | 5 | 5 | **5** | 5.56 (5.48–5.70) | 8.82 (8.56–9.96) | 9.96 |
| Sonnet 4.5 alone | 5 | 5 | 5 | 5 | **5** | 5.79 (5.72–5.80) | 10.16 (10.03–10.34) | 10.34 |
| RepoOMP's published Claude program (repoomp_published) | 1 | 1 | 1 | 1 | **1** | 5.73 | 10.05 | 10.05 |
| RepoOMP's Claude Code program | 1 | 0 | 0 | 0 | **0** | 5.81 | 10.38 | 10.38 |
| NPB's OpenMP version | 1 | 1 | 0 | 1 | **0** | 5.79 | 10.33 | 10.33 |

Race check, every program not clean (verdict = the first stage that failed; ThreadSanitizer's own result beside it):

- RepoOMP's Claude Code program rep1: `tsan`, ThreadSanitizer race; the race: `r` — cg.c line(s) 205, 211, 217 in the report; the name stands on line(s) 22, 27, 103, 109, 131, 142, 196, 211, 212, 217, 244, 246, 252, 266, 270 of the final cg.c
- NPB's OpenMP version rep1: `tsan`, ThreadSanitizer race; the race: `callcount` — cg.c line(s) 209, 405, 540 in the report; the name stands on line(s) 366, 540 of the final cg.c

### (3) The headline

The agent reached a usable program in 5 of 5 trials; RepoOMP's published program is usable (one program, possibly its best of several). Speedup at 6 / 12 threads — the agent's usable trials: median 5.56 (5.48–5.70) / 8.82 (8.56–9.96), best 9.96; RepoOMP's: 5.73 / 10.05.

### (4) Calls, cost, BROKEN by cause

| setup | trials | calls | failed calls | cost (USD) | per trial | BROKEN: not repeatable | values outside 1e-9 | does not build |
|---|---|---|---|---|---|---|---|---|
| DiscoPoP alone | 5 | 0 | 0 | 0.00 | 0.00 | 0 | 0 | 0 |
| the agent | 5 | 35 | 0 | 22.63 | 4.53 | 0 | 0 | 0 |
| Sonnet 4.5 alone | 5 | 5 | 0 | 1.95 | 0.39 | 0 | 0 | 0 |

### Every trial

| setup | rep | outcome | race check | NPB 2nd class | usable | 6 / 12 thr | BROKEN cause | calls | cost |
|---|---|---|---|---|---|---|---|---|---|
| DiscoPoP alone | 1 | FASTER | clean | SUCCESSFUL | yes | 5.36 / 9.13 | — | 0 | 0.00 |
| DiscoPoP alone | 2 | FASTER | clean | SUCCESSFUL | yes | 5.80 / 10.14 | — | 0 | 0.00 |
| DiscoPoP alone | 3 | FASTER | clean | SUCCESSFUL | yes | 5.76 / 10.04 | — | 0 | 0.00 |
| DiscoPoP alone | 4 | FASTER | clean | SUCCESSFUL | yes | 5.70 / 9.96 | — | 0 | 0.00 |
| DiscoPoP alone | 5 | FASTER | clean | SUCCESSFUL | yes | 5.24 / 8.48 | — | 0 | 0.00 |
| the agent | 1 | FASTER | clean | SUCCESSFUL | yes | 5.48 / 8.56 | — | 8 | 5.06 |
| the agent | 2 | FASTER | clean | SUCCESSFUL | yes | 5.49 / 8.60 | — | 9 | 9.27 |
| the agent | 3 | FASTER | clean | SUCCESSFUL | yes | 5.70 / 9.96 | — | 7 | 3.62 |
| the agent | 4 | FASTER | clean | SUCCESSFUL | yes | 5.56 / 9.62 | — | 4 | 1.62 |
| the agent | 5 | FASTER | clean | SUCCESSFUL | yes | 5.58 / 8.82 | — | 7 | 3.06 |
| Sonnet 4.5 alone | 1 | FASTER | clean | SUCCESSFUL | yes | 5.79 / 10.27 | — | 1 | 0.38 |
| Sonnet 4.5 alone | 2 | FASTER | clean | SUCCESSFUL | yes | 5.78 / 10.05 | — | 1 | 0.36 |
| Sonnet 4.5 alone | 3 | FASTER | clean | SUCCESSFUL | yes | 5.79 / 10.16 | — | 1 | 0.41 |
| Sonnet 4.5 alone | 4 | FASTER | clean | SUCCESSFUL | yes | 5.72 / 10.03 | — | 1 | 0.42 |
| Sonnet 4.5 alone | 5 | FASTER | clean | SUCCESSFUL | yes | 5.80 / 10.34 | — | 1 | 0.38 |
| RepoOMP's published Claude program (repoomp_published) | 1 | FASTER | clean | SUCCESSFUL | yes | 5.73 / 10.05 | — | 0 | 0.00 |
| RepoOMP's Claude Code program | 1 | BROKEN | tsan | UNSUCCESSFUL | no | 5.81 / 10.38 | values outside 1e-9 | 0 | 0.00 |
| NPB's OpenMP version | 1 | FASTER | tsan | SUCCESSFUL | no | 5.79 / 10.33 | — | 0 | 0.00 |

### (5) The directives of each usable program

- DiscoPoP alone rep1 (DiscoPoP 10, model 0):
    - `89: #pragma omp parallel for firstprivate(j)  →  for (k = rowstr[j]; k < rowstr[j+1]; k++) {`
    - `97: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `110: #pragma omp parallel for reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `120: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `131: #pragma omp parallel for reduction(+:norm_temp12,norm_temp11)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `142: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `203: #pragma omp parallel for shared(p,r,x,q,z)  →  for (j = 1; j <= naa+1; j++) {`
    - `220: #pragma omp parallel for private(sum,k) shared(q,colidx,rowstr,a,p)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `241: #pragma omp parallel for firstprivate(beta) shared(r)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `250: #pragma omp parallel for private(d,k) shared(r,colidx,rowstr,a,z)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
- DiscoPoP alone rep2 (DiscoPoP 14, model 0):
    - `89: #pragma omp parallel for firstprivate(j)  →  for (k = rowstr[j]; k < rowstr[j+1]; k++) {`
    - `94: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `116: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `121: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `132: #pragma omp parallel for reduction(+:norm_temp12,norm_temp11)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `143: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `204: #pragma omp parallel for shared(p,r,x,q,z)  →  for (j = 1; j <= naa+1; j++) {`
    - `212: #pragma omp parallel for shared(r) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `222: #pragma omp parallel for private(sum,k) shared(q,colidx,rowstr,a,p)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `231: #pragma omp parallel for shared(p,q) reduction(+:d)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `236: #pragma omp parallel for firstprivate(alpha) shared(r,z) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `245: #pragma omp parallel for firstprivate(beta) shared(r)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `254: #pragma omp parallel for private(d,k) shared(r,colidx,rowstr,a,z)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
- DiscoPoP alone rep3 (DiscoPoP 11, model 0):
    - `89: #pragma omp parallel for firstprivate(j)  →  for (k = rowstr[j]; k < rowstr[j+1]; k++) {`
    - `97: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `110: #pragma omp parallel for reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `130: #pragma omp parallel for reduction(+:norm_temp12,norm_temp11)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `141: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `202: #pragma omp parallel for shared(p,r,x,q,z)  →  for (j = 1; j <= naa+1; j++) {`
    - `210: #pragma omp parallel for shared(r) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `220: #pragma omp parallel for private(sum,k) shared(q,colidx,rowstr,a,p)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `233: #pragma omp parallel for firstprivate(alpha) shared(r,z) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `242: #pragma omp parallel for firstprivate(beta) shared(r)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `251: #pragma omp parallel for private(d,k) shared(r,colidx,rowstr,a,z)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
- DiscoPoP alone rep4 (DiscoPoP 14, model 0):
    - `89: #pragma omp parallel for firstprivate(j)  →  for (k = rowstr[j]; k < rowstr[j+1]; k++) {`
    - `94: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `111: #pragma omp parallel for reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `117: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `122: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `133: #pragma omp parallel for reduction(+:norm_temp12,norm_temp11)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `144: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `205: #pragma omp parallel for shared(p,r,x,q,z)  →  for (j = 1; j <= naa+1; j++) {`
    - `213: #pragma omp parallel for shared(r) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `223: #pragma omp parallel for private(sum,k) shared(q,colidx,rowstr,a,p)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `236: #pragma omp parallel for firstprivate(alpha) shared(r,z) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `245: #pragma omp parallel for firstprivate(beta) shared(r)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `254: #pragma omp parallel for private(d,k) shared(r,colidx,rowstr,a,z)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
- DiscoPoP alone rep5 (DiscoPoP 11, model 0):
    - `89: #pragma omp parallel for firstprivate(j)  →  for (k = rowstr[j]; k < rowstr[j+1]; k++) {`
    - `94: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `111: #pragma omp parallel for reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `117: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `122: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `133: #pragma omp parallel for reduction(+:norm_temp12,norm_temp11)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `144: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `205: #pragma omp parallel for shared(p,r,x,q,z)  →  for (j = 1; j <= naa+1; j++) {`
    - `222: #pragma omp parallel for private(sum,k) shared(q,colidx,rowstr,a,p)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `251: #pragma omp parallel for private(d,k) shared(r,colidx,rowstr,a,z)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
- the agent rep1 (DiscoPoP 9, model 0):
    - `89: #pragma omp parallel for firstprivate(j)  →  for (k = rowstr[j]; k < rowstr[j+1]; k++) {`
    - `94: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `111: #pragma omp parallel for reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `131: #pragma omp parallel for reduction(+:norm_temp12,norm_temp11)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `142: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `203: #pragma omp parallel for shared(p,r,x,q,z)  →  for (j = 1; j <= naa+1; j++) {`
    - `220: #pragma omp parallel for private(sum,k) shared(q,colidx,rowstr,a,p)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `249: #pragma omp parallel for private(d,k) shared(r,colidx,rowstr,a,z)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
- the agent rep2 (DiscoPoP 11, model 0):
    - `89: #pragma omp parallel for firstprivate(j)  →  for (k = rowstr[j]; k < rowstr[j+1]; k++) {`
    - `94: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `111: #pragma omp parallel for reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `117: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `122: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `133: #pragma omp parallel for reduction(+:norm_temp12,norm_temp11)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `144: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `205: #pragma omp parallel for shared(p,r,x,q,z)  →  for (j = 1; j <= naa+1; j++) {`
    - `222: #pragma omp parallel for private(sum,k) shared(q,colidx,rowstr,a,p)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `251: #pragma omp parallel for private(d,k) shared(r,colidx,rowstr,a,z)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
- the agent rep3 (DiscoPoP 10, model 0):
    - `89: #pragma omp parallel for firstprivate(j)  →  for (k = rowstr[j]; k < rowstr[j+1]; k++) {`
    - `97: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `119: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `130: #pragma omp parallel for reduction(+:norm_temp12,norm_temp11)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `141: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `202: #pragma omp parallel for shared(p,r,x,q,z)  →  for (j = 1; j <= naa+1; j++) {`
    - `219: #pragma omp parallel for private(sum,k) shared(q,colidx,rowstr,a,p)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `232: #pragma omp parallel for firstprivate(alpha) shared(r,z) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `241: #pragma omp parallel for firstprivate(beta) shared(r)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `250: #pragma omp parallel for private(d,k) shared(r,colidx,rowstr,a,z)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
- the agent rep4 (DiscoPoP 11, model 0):
    - `89: #pragma omp parallel for firstprivate(j)  →  for (k = rowstr[j]; k < rowstr[j+1]; k++) {`
    - `94: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `111: #pragma omp parallel for reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `117: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `142: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `203: #pragma omp parallel for shared(p,r,x,q,z)  →  for (j = 1; j <= naa+1; j++) {`
    - `220: #pragma omp parallel for private(sum,k) shared(q,colidx,rowstr,a,p)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `229: #pragma omp parallel for shared(p,q) reduction(+:d)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `242: #pragma omp parallel for firstprivate(beta) shared(r)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `251: #pragma omp parallel for private(d,k) shared(r,colidx,rowstr,a,z)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
- the agent rep5 (DiscoPoP 11, model 0):
    - `89: #pragma omp parallel for firstprivate(j)  →  for (k = rowstr[j]; k < rowstr[j+1]; k++) {`
    - `94: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `116: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `121: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `132: #pragma omp parallel for reduction(+:norm_temp12,norm_temp11)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `143: #pragma omp parallel for firstprivate(norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `204: #pragma omp parallel for shared(p,r,x,q,z)  →  for (j = 1; j <= naa+1; j++) {`
    - `221: #pragma omp parallel for private(sum,k) shared(q,colidx,rowstr,a,p)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `230: #pragma omp parallel for shared(p,q) reduction(+:d)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `251: #pragma omp parallel for private(d,k) shared(r,colidx,rowstr,a,z)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
- Sonnet 4.5 alone rep1:
    - `88: #pragma omp parallel for private(j, k)  →  for (j = 1; j <= lastrow - firstrow + 1; j++) {`
    - `94: #pragma omp parallel for private(i)  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for private(j)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `111: #pragma omp parallel for private(j) reduction(+:norm_temp11, norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `117: #pragma omp parallel for private(j)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `122: #pragma omp parallel for private(i)  →  for (i = 1; i <= NA+1; i++) {`
    - `133: #pragma omp parallel for private(j) reduction(+:norm_temp11, norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `144: #pragma omp parallel for private(j)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `205: #pragma omp parallel for private(j)  →  for (j = 1; j <= naa+1; j++) {`
    - `213: #pragma omp parallel for private(j) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `223: #pragma omp parallel for private(j, k, sum)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `232: #pragma omp parallel for private(j) reduction(+:d)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `237: #pragma omp parallel for private(j) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `246: #pragma omp parallel for private(j)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `255: #pragma omp parallel for private(j, k, d)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `263: #pragma omp parallel for private(j, d) reduction(+:sum)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
- Sonnet 4.5 alone rep2:
    - `88: #pragma omp parallel for private(k)  →  for (j = 1; j <= lastrow - firstrow + 1; j++) {`
    - `94: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `111: #pragma omp parallel for reduction(+:norm_temp11, norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `117: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `122: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `133: #pragma omp parallel for reduction(+:norm_temp11, norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `144: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `205: #pragma omp parallel for  →  for (j = 1; j <= naa+1; j++) {`
    - `213: #pragma omp parallel for reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `223: #pragma omp parallel for private(sum, k)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `232: #pragma omp parallel for reduction(+:d)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `237: #pragma omp parallel for reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `246: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `255: #pragma omp parallel for private(d, k)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `263: #pragma omp parallel for private(d) reduction(+:sum)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
- Sonnet 4.5 alone rep3:
    - `88: #pragma omp parallel for private(k)  →  for (j = 1; j <= lastrow - firstrow + 1; j++) {`
    - `94: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `111: #pragma omp parallel for reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `117: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `122: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `133: #pragma omp parallel for reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `144: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `205: #pragma omp parallel for  →  for (j = 1; j <= naa+1; j++) {`
    - `213: #pragma omp parallel for reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `223: #pragma omp parallel for private(sum,k)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `232: #pragma omp parallel for reduction(+:d)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `237: #pragma omp parallel for reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `246: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `255: #pragma omp parallel for private(d,k)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `263: #pragma omp parallel for private(d) reduction(+:sum)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
- Sonnet 4.5 alone rep4:
    - `88: #pragma omp parallel for private(j, k)  →  for (j = 1; j <= lastrow - firstrow + 1; j++) {`
    - `94: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `111: #pragma omp parallel for reduction(+:norm_temp11, norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `117: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `122: #pragma omp parallel for  →  for (i = 1; i <= NA+1; i++) {`
    - `133: #pragma omp parallel for reduction(+:norm_temp11, norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `144: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `150: #pragma omp parallel  →  {`
    - `152: #pragma omp master  →  nthreads = omp_get_num_threads();`
    - `207: #pragma omp parallel for  →  for (j = 1; j <= naa+1; j++) {`
    - `215: #pragma omp parallel for reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `225: #pragma omp parallel for private(sum, k)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `234: #pragma omp parallel for reduction(+:d)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `239: #pragma omp parallel for reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `248: #pragma omp parallel for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `257: #pragma omp parallel for private(d, k)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `265: #pragma omp parallel for private(d) reduction(+:sum)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
- Sonnet 4.5 alone rep5:
    - `88: #pragma omp parallel for private(j,k) collapse(2)  →  for (j = 1; j <= lastrow - firstrow + 1; j++) {`
    - `94: #pragma omp parallel for private(i)  →  for (i = 1; i <= NA+1; i++) {`
    - `98: #pragma omp parallel for private(j)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `111: #pragma omp parallel for private(j) reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `117: #pragma omp parallel for private(j)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `122: #pragma omp parallel for private(i)  →  for (i = 1; i <= NA+1; i++) {`
    - `133: #pragma omp parallel for private(j) reduction(+:norm_temp11,norm_temp12)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `144: #pragma omp parallel for private(j)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `205: #pragma omp parallel for private(j)  →  for (j = 1; j <= naa+1; j++) {`
    - `213: #pragma omp parallel for private(j) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `223: #pragma omp parallel for private(j,k,sum)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `232: #pragma omp parallel for private(j) reduction(+:d)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `237: #pragma omp parallel for private(j) reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `246: #pragma omp parallel for private(j)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `255: #pragma omp parallel for private(j,k,d)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `263: #pragma omp parallel for private(j,d) reduction(+:sum)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
- RepoOMP's published Claude program (repoomp_published) rep1:
    - `208: #pragma omp parallel shared(a, p, q, z, r, colidx, rowstr, firstrow, lastrow, firstcol, lastcol) private(j, k)  →  {`
    - `211: #pragma omp for schedule(static)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `220: #pragma omp single  →  {`
    - `225: #pragma omp for reduction(+:d)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `230: #pragma omp single  →  {`
    - `235: #pragma omp single  →  {`
    - `240: #pragma omp for reduction(+:rho)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `247: #pragma omp single  →  {`
    - `252: #pragma omp for  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`
    - `260: #pragma omp parallel  →  {`
    - `263: #pragma omp for private(d_local, k)  →  for (j = 1; j <= lastrow-firstrow+1; j++) {`
    - `271: #pragma omp for private(d_local) reduction(+:sum)  →  for (j = 1; j <= lastcol-firstcol+1; j++) {`

