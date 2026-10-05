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
        /* xx[i+1] == flat_2d_array[i + vl + 1]: a recurrence of distance vl+1 = 64.
         * Indices split into vl+1 independent chains (by i mod (vl+1)); each chain is
         * walked sequentially in its original order, chains run in parallel. */
#pragma omp parallel for shared(xx, flat_2d_array, a) firstprivate(vl) schedule(static)
        for (int r = 0; r < vl + 1; r++) {
            for (int i = r; i < LEN_1D - 1; i += vl + 1) {
                xx[i+1] = flat_2d_array[i] + a[i];
            }
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s424)
