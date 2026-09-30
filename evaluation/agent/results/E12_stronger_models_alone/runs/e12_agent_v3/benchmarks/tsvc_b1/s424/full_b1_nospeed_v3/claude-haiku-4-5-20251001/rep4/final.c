/* TSVC-2 loop s424, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s424.h"

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

static real_t kernel_s424(void)
{
    int vl = 63;
    xx = flat_2d_array + vl;
    for (int nl = 0; nl < R; nl++) {
        // Stage 0: iterations 0-63 (no earlier iteration to depend on)
        for (int i = 0; i < 64 && i < LEN_1D - 1; i++) {
            xx[i+1] = flat_2d_array[i] + a[i];
        }
        // Stages 1+: iterations 64-end, in groups of 64 (each iteration depends only on prior stage)
        #pragma omp parallel
        #pragma omp single
        {
        #pragma omp task
        #pragma omp task
        for (int stage = 1; stage * 64 < LEN_1D - 1; stage++) {
            for (int i = stage * 64; i < (stage + 1) * 64 && i < LEN_1D - 1; i++) {
                xx[i+1] = flat_2d_array[i] + a[i];
            }
        }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s424)
