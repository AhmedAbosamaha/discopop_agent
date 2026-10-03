/* TSVC-2 loop s244, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s244.h"

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

static real_t kernel_s244(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* The write to a[i+1] in iteration i is overwritten by iteration i+1
         * before it is read, so it is dead for every i except the last one.
         * Compute the independent part in parallel, then apply the single
         * surviving a[LEN_1D-1] update afterwards. */
#pragma omp parallel for default(none) shared(a, b, c, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        if (LEN_1D >= 2) {
            int last = LEN_1D-2;
            a[last+1] = b[last] + a[last+1] * d[last];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s244)
