/* TSVC-2 loop s212, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s212.h"

/* Between two repetitions a few INPUT elements change, so no repetition can be skipped,
 * merged with another or run out of order: the repetition loop is sequential by a true
 * dependence, and the loop under study is the one inside it. */
static void pb_mix(int nl)
{
  long k = ((long)nl * 7919L + 13L) % LEN_1D;
  a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
  d[k] += (real_t)0.125; e[k] += (real_t)0.25;
  a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
}

static real_t kernel_s212(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* The original single loop carries a true dependence: iteration i reads
         * a[i+1], which iteration i+1 has not yet overwritten (sequential order
         * runs i before i+1), so b[i] always sees the pre-multiply value of
         * a[i+1]. Splitting into two passes reproduces that ordering exactly
         * without extra storage: pass 1 reads all of a[] (still unmodified)
         * to update b[], and only after pass 1 fully completes does pass 2
         * overwrite a[] in place. Each pass now touches disjoint indices per
         * iteration (b[i] in pass 1, a[i] in pass 2), so both are safe to
         * run in parallel in any order/schedule, as long as pass 1 finishes
         * before pass 2 starts (enforced by being separate loops). */
        #pragma omp parallel for default(none) shared(a, b, d)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }
        #pragma omp parallel for default(none) shared(a, c)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s212)
