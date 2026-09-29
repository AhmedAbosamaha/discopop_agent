/* TSVC-2 loop s277, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s277.h"

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

static real_t kernel_s277(void)
{
    /* Allocate temporary buffers to break loop-carried dependencies on both a and b.
       Reading from original values and writing to independent buffer locations makes
       all iterations fully independent for parallel execution. */
    real_t *a_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *b_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Initialize temporary buffers with original values */
        for (int i = 0; i < LEN_1D; i++) {
            a_temp[i] = a[i];
            b_temp[i] = b[i];
        }

        /* Parallel loop: each iteration reads original array values and writes to independent locations.
           Loop-carried dependence is broken by reading from original arrays (a, b) and writing to
           temporary buffers (a_temp for a[i] updates, b_temp for b[i+1] writes).
           Data sharing: shared arrays (a, b, c, d, e, a_temp, b_temp) are read/written by independent iterations. */
        #pragma omp parallel for \
            shared(a, b, a_temp, b_temp, c, d, e)
        for (int i = 0; i < LEN_1D-1; i++) {
                if (a[i] >= (real_t)0.) {
                    /* Skip update, a_temp[i] keeps original value from initialization */
                } else if (b[i] >= (real_t)0.) {
                    /* Skip a update, perform b update */
                    b_temp[i+1] = c[i] + d[i] * e[i];
                } else {
                    /* Perform both updates */
                    a_temp[i] += c[i] * d[i];
                    b_temp[i+1] = c[i] + d[i] * e[i];
                }
        }

        /* Copy temporary buffers back to original arrays */
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = a_temp[i];
        }
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = b_temp[i];
        }

        pb_mix(nl);
    }

    free(a_temp);
    free(b_temp);
    return (real_t)0;
}

PB_MAIN(kernel_s277)
