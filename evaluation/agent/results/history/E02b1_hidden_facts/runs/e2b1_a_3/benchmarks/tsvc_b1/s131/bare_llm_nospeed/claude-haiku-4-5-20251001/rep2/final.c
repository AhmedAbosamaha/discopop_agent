/* TSVC-2 loop s131, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s131.h"

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

static real_t kernel_s131(void)
{
    int m  = 1;
    for (int nl = 0; nl < R; nl++) {
        /* Save input array to eliminate forward dependence:
         * iteration i needs a[i+1] but iteration i+1 will overwrite it.
         * By reading from a saved copy, all iterations become independent. */
        real_t *a_save = malloc(LEN_1D * sizeof(real_t));
        for (int j = 0; j < LEN_1D; j++) {
            a_save[j] = a[j];
        }

        /* Parallelize inner loop: each iteration i reads from a_save[i+1] (read-only)
         * and writes to a[i] (disjoint elements, no conflicts). */
        #pragma omp parallel for shared(a, a_save, b, m)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i] = a_save[i + m] + b[i];
        }

        free(a_save);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s131)
