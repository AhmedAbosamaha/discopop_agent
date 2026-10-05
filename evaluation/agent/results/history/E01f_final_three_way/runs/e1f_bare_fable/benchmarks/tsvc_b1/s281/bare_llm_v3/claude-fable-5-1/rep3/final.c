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
    /* Split point: iterations i < mid read a[LEN_1D-i-1] with LEN_1D-i-1 >= LEN_1D-mid,
     * which no other iteration of the first loop writes (the odd-length middle element is
     * read and written only within its own iteration).  Iterations i >= mid read
     * a[LEN_1D-i-1] with LEN_1D-i-1 < mid, i.e. values finalized by the first loop. */
    const int mid = (LEN_1D + 1) / 2;
    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for private(x) shared(a, b, c) schedule(static)
        for (int i = 0; i < mid; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        #pragma omp parallel for private(x) shared(a, b, c) schedule(static)
        for (int i = mid; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s281)
