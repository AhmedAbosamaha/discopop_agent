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
    const int half = (LEN_1D + 1) / 2;
    for (int nl = 0; nl < R; nl++) {
        /* First half: a[LEN_1D-i-1] has index >= LEN_1D/2, i.e. an element not
         * written by any other iteration of this loop (original value). */
#pragma omp parallel for private(x) schedule(static)
        for (int i = 0; i < half; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        /* Second half: a[LEN_1D-i-1] has index < LEN_1D/2, already finalized by
         * the loop above; writes go to a[i] in the disjoint upper range. */
#pragma omp parallel for private(x) schedule(static)
        for (int i = half; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s281)
