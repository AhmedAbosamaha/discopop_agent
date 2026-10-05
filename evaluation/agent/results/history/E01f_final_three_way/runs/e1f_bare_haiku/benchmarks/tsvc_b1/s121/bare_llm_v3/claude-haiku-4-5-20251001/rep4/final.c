/* TSVC-2 loop s121, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s121.h"

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

static real_t kernel_s121(void)
{
    int j;
    for (int nl = 0; nl < R; nl++) {
        /* Allocate temporary buffer to save original array values */
        real_t *a_tmp = malloc(LEN_1D * sizeof(real_t));
        /* Copy original values to avoid anti-dependence */
        memcpy(a_tmp, a, LEN_1D * sizeof(real_t));

        /* Parallel loop: all iterations are now independent.
         * Each iteration reads from a_tmp (read-only, shared) and writes to a (different locations, private writes).
         * i: loop variable, shared
         * j: per-iteration temporary, private
         * a_tmp: shared read-only data
         * b: shared read-only data
         * a: written to different locations, effectively private per iteration
         */
        #pragma omp parallel for schedule(static) private(j) shared(a_tmp, b, a)
        for (int i = 0; i < LEN_1D-1; i++) {
            j = i + 1;
            a[i] = a_tmp[j] + b[i];
        }

        free(a_tmp);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s121)
