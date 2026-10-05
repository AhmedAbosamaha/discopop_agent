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
        /* Allocate temporary buffer to break anti-dependence:
         * iteration i reads a[i+1], iteration i+1 writes a[i+1].
         * Save original values so all parallel iterations read the same snapshot. */
        real_t *a_temp = (real_t *)malloc(sizeof(real_t) * (LEN_1D - 1));

        /* Copy phase: independent loop, each iteration reads a[i+m] and writes to a_temp[i] */
        #pragma omp parallel for shared(a, a_temp, m)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a_temp[i] = a[i + m];
        }

        /* Computation phase: independent loop, each iteration reads a_temp[i], b[i]
         * and writes to a[i]. No anti-dependence now since all threads read from snapshot. */
        #pragma omp parallel for shared(a, a_temp, b)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i] = a_temp[i] + b[i];
        }

        free(a_temp);
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s131)
