/* TSVC-2 loop s1213, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s1213.h"

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

static real_t kernel_s1213(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Make copies of initial a[] and b[] to break loop-carried dependencies.
         * Iteration i reads from a_init[i+1] and b_init[i-1] (initial values, no loop-carried dep).
         * Iteration i writes to a[i] and b[i] (distinct elements, no write conflicts).
         */
        real_t *a_init = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *b_init = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(a_init, a, LEN_1D * sizeof(real_t));
        memcpy(b_init, b, LEN_1D * sizeof(real_t));

        #pragma omp parallel for schedule(static) shared(a, b, c, d, a_init, b_init)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b_init[i-1]+c[i];
            b[i] = a_init[i+1]*d[i];
        }

        free(a_init);
        free(b_init);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s1213)
