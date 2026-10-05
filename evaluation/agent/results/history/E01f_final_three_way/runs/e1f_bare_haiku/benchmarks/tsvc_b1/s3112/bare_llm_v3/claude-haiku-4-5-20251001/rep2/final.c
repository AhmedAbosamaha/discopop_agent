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
    real_t *prefix, *temp;

    for (int nl = 0; nl < R; nl++) {
        sum = (real_t)0.0;

        /* Allocate temporary arrays for parallel prefix sum computation */
        prefix = (real_t *)malloc(LEN_1D * sizeof(real_t));
        temp = (real_t *)malloc(LEN_1D * sizeof(real_t));

        /* Initialize prefix array with input values a[i]
         * Each element will become the inclusive prefix sum */
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            prefix[i] = a[i];
        }

        /* Parallel inclusive scan: up-sweep phase
         * Each stage s computes prefix sums for distances 2^s apart
         * Iterations within each stage are independent: iteration i only
         * reads prefix[i-s], which was finalized in the previous stage.
         * Use temp array to avoid races when updating in parallel. */
        for (int s = 1; s < LEN_1D; s *= 2) {
            #pragma omp parallel for
            for (int i = s; i < LEN_1D; i++) {
                temp[i] = prefix[i] + prefix[i - s];
            }
            #pragma omp parallel for
            for (int i = s; i < LEN_1D; i++) {
                prefix[i] = temp[i];
            }
        }

        /* Copy prefix sums to output array b in parallel
         * Each iteration is independent: b[i] = prefix[i] */
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = prefix[i];
        }

        /* Extract final sum (inclusive prefix of all elements) */
        sum = prefix[LEN_1D - 1];

        free(prefix);
        free(temp);
        pb_mix(nl);
    }
    return sum;
}

PB_MAIN(kernel_s3112)
