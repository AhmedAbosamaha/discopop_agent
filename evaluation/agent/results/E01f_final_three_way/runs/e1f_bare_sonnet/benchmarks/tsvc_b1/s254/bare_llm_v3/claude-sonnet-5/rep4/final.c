/* TSVC-2 loop s254, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s254.h"

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

static real_t kernel_s254(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Original recurrence: x carried b[i-1] (with b[LEN_1D-1] wrapping in for i==0)
         * from one iteration to the next, but produced no other value. Replaced the
         * carried x with a direct read of the previous element (or the wrap value at
         * i==0), which removes the loop-carried dependence: a[] is write-only and b[]
         * is read-only inside this loop, so iterations are now independent. */
        #pragma omp parallel for schedule(static) shared(a, b)
        for (int i = 0; i < LEN_1D; i++) {
            real_t prev = (i == 0) ? b[LEN_1D-1] : b[i-1];
            a[i] = (b[i] + prev) * (real_t).5;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s254)
