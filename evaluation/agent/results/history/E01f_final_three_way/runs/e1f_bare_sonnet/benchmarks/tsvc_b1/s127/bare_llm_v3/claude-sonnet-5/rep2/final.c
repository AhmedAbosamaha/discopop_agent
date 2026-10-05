/* TSVC-2 loop s127, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s127.h"

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

static real_t kernel_s127(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* j was an induction variable incremented twice per iteration starting at -1,
         * so at iteration i its two values are exactly 2*i and 2*i+1 -- a closed form
         * that lets each iteration's writes (a[2*i], a[2*i+1]) be computed independently
         * of every other iteration, removing the carried dependence on j. */
        #pragma omp parallel for default(none) shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D/2; i++) {
            a[2*i] = b[i] + c[i] * d[i];
            a[2*i+1] = b[i] + d[i] * e[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s127)
