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
    /* Iteration i reads a[LEN_1D-i-1] and writes a[i].  For i in the first half the
     * mirrored element is still unwritten (it lies in the second half, or is a[i]
     * itself for the middle element of an odd length); for i in the second half it
     * was already written by iteration LEN_1D-i-1 of the first half.  Running the
     * first half to completion before the second half preserves that value flow,
     * and within each half no two iterations touch the same location. */
    const int half = (LEN_1D + 1) / 2;
    for (int nl = 0; nl < R; nl++) {
#pragma omp parallel for private(x) shared(a, b, c)
        for (int i = 0; i < half; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
#pragma omp parallel for private(x) shared(a, b, c)
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
