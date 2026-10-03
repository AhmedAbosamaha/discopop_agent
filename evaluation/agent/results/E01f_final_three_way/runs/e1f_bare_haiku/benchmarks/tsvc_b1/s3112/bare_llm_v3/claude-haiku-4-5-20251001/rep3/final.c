/* TSVC-2 loop s3112, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s3112.h"

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

static real_t kernel_s3112(void)
{
    real_t sum;
    real_t *b_temp = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Initialize b with values from a (parallelizable).
           Each iteration i writes to b[i], reading only a[i]. */
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = a[i];
        }

        /* Parallel prefix sum using logarithmic-depth doubling.
           In each phase d, compute b[i] = b[i] + b[i-d] in parallel.
           The temporary buffer b_temp avoids data races: each iteration
           reads OLD b values and writes NEW values to b_temp, then we copy back.
           After log(LEN_1D) phases, b contains the cumulative sum. */
        for (int d = 1; d < LEN_1D; d *= 2) {
            /* Phase 1: Compute new values in temporary buffer.
               Each iteration i >= d reads b[i] and b[i-d] from the CURRENT phase
               state, then writes to b_temp[i]. This avoids read-write races. */
            #pragma omp parallel for
            for (int i = 0; i < LEN_1D; i++) {
                b_temp[i] = (i >= d) ? (b[i] + b[i - d]) : b[i];
            }

            /* Phase 2: Copy results back to b.
               Each iteration i writes b[i] from b_temp[i]. */
            #pragma omp parallel for
            for (int i = 0; i < LEN_1D; i++) {
                b[i] = b_temp[i];
            }
        }

        /* After the parallel prefix sum, b[LEN_1D-1] contains the total sum. */
        sum = b[LEN_1D - 1];

        pb_mix(nl);
    }

    free(b_temp);
    return sum;
}

PB_MAIN(kernel_s3112)
