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
    real_t *new_b = malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < R; nl++) {
        // Phase 1: compute new b values (parallel-ready: no loop-carried dependence)
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D-1; i++) {
            new_b[i] = a[i+1]*d[i];
        }
        // Phase 2: update b array with newly computed values (parallel-ready)
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = new_b[i];
        }
        // Phase 3: compute a values using updated b (sequential: reads b[i-1] computed by i-1)
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }
        pb_mix(nl);
    }

    free(new_b);
    return (real_t)0;
}

PB_MAIN(kernel_s1213)
