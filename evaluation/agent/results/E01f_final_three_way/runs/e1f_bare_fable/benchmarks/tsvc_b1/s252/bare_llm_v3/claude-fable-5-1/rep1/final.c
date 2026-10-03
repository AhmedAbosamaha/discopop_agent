/* TSVC-2 loop s252, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s252.h"

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

static real_t kernel_s252(void)
{
    real_t t, s;
    for (int nl = 0; nl < R; nl++) {
        /* Peeled first iteration: t starts at 0. */
        t = (real_t) 0.;
        s = b[0] * c[0];
        a[0] = s + t;
        /* The carried value t is just the previous product b[i-1]*c[i-1];
         * recompute it per iteration so iterations are independent. */
#pragma omp parallel for default(none) shared(a, b, c) private(s, t) schedule(static)
        for (int i = 1; i < LEN_1D; i++) {
            t = b[i - 1] * c[i - 1];
            s = b[i] * c[i];
            a[i] = s + t;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s252)
