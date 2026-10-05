/* TSVC-2 loop s281, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s281.h"

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

static real_t kernel_s281(void)
{
    real_t x;
    /* Temporary buffer to hold intermediate x values. Allocated on heap since
     * LEN_1D can be very large (up to 192000000). Each iteration computes x and
     * stores it here, then a second parallelized loop writes to a[] and b[]. This
     * splits the loop to move inter-iteration dependencies between loops rather than
     * within a loop, allowing parallel execution.*/
    real_t *x_vals = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* First pass: read from unmodified arrays a, b, c and compute x values.
         * No iteration reads data written by another iteration in this loop because
         * a and b are not modified here. Variable x is private (declared in loop body
         * implicitly via x_vals[i] assignment).*/
        #pragma omp parallel for private(x)
        for (int i = 0; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            x_vals[i] = x;
        }

        /* Second pass: write computed values to arrays a and b. Each iteration i
         * writes only to a[i] and b[i], so no iteration depends on another's writes.
         * Variable x is private (local to each iteration).*/
        #pragma omp parallel for private(x)
        for (int i = 0; i < LEN_1D; i++) {
            x = x_vals[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        pb_mix(nl);
    }

    free(x_vals);
    return (real_t)0;
}

PB_MAIN(kernel_s281)
