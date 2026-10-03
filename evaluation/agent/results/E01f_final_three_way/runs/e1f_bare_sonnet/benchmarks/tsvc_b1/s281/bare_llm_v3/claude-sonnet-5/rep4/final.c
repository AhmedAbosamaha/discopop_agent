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
    int n = LEN_1D;
    int half = n / 2;
    for (int nl = 0; nl < R; nl++) {
        /* Original loop couples index i with its mirror LEN_1D-1-i: the mirror's
         * old value is read, then overwritten, and later in the same pass the
         * mirror reads back the fresh value written at i. Regroup the pass into
         * independent (lo, hi) pairs with hi = n-1-lo: each pair reproduces,
         * in the same order, exactly the two reads/writes the original run
         * performed for indices lo and hi, so pairs no longer depend on each
         * other and can run in any order/on any thread. */
        #pragma omp parallel for default(none) shared(a, b, c, n, half)
        for (int lo = 0; lo < half; lo++) {
            int hi = n - 1 - lo;
            real_t aHi = a[hi];
            real_t xlo = aHi + b[lo] * c[lo];
            a[lo] = xlo - (real_t)1.0;
            b[lo] = xlo;
            real_t xhi = a[lo] + b[hi] * c[hi];
            a[hi] = xhi - (real_t)1.0;
            b[hi] = xhi;
        }
        if (n % 2 == 1) {
            int mid = half;
            x = a[mid] + b[mid] * c[mid];
            a[mid] = x - (real_t)1.0;
            b[mid] = x;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s281)
