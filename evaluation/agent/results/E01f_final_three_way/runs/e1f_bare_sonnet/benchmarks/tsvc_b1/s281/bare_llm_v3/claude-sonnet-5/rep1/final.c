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
    /* Within one activation of the i-loop, a[i] is written and a[LEN_1D-i-1]
     * is read. For i < mid the mirror index has not been written yet this
     * activation (read sees the pre-activation value); for i >= mid the
     * mirror index was already written earlier in this same activation
     * (read must see the freshly computed value). Splitting at mid into two
     * parallel regions with the implicit barrier between them reproduces
     * that exact ordering: all of [0,mid) is finished (and its writes are
     * visible) before [mid,LEN_1D) starts reading from it. Iterations
     * within each half only write their own a[i]/b[i] and read from the
     * other, untouched-by-this-half, index range, so they are mutually
     * independent. */
    const int mid = LEN_1D / 2;
    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for shared(a, b, c, mid)
        for (int i = 0; i < mid; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        #pragma omp parallel for shared(a, b, c, mid)
        for (int i = mid; i < LEN_1D; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s281)
