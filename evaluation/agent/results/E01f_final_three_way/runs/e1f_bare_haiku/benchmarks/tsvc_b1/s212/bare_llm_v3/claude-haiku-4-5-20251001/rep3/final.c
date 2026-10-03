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
        /* Save original a[] values before any modifications to enable parallelization:
         * iteration i reads a[i+1], which must be the original value (before iteration i+1
         * modifies it). By saving a copy first, both phases can run in parallel safely. */
        real_t *a_orig = malloc(sizeof(real_t) * LEN_1D);
        memcpy(a_orig, a, sizeof(real_t) * LEN_1D);

        /* Phase 1: Parallelize multiplication of a[]. Each iteration i writes only to a[i],
         * so there are no conflicts between iterations. */
        #pragma omp parallel for shared(a, c)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }

        /* Phase 2: Parallelize update of b[] using original a values. Each iteration i
         * reads a_orig[i+1] (original value) and d[i], and writes to b[i]. No conflicts. */
        #pragma omp parallel for shared(b, a_orig, d)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a_orig[i + 1] * d[i];
        }

        free(a_orig);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s212)
