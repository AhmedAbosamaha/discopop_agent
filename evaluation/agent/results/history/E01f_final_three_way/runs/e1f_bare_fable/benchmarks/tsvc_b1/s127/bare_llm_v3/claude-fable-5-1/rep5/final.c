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
    int j;
    for (int nl = 0; nl < R; nl++) {
        j = -1;
        /* The induction variable j is 2*i / 2*i+1 in closed form, so each
         * iteration owns a[2i] and a[2i+1] exclusively; b,c,d,e are read-only. */
#pragma omp parallel for shared(a, b, c, d, e) schedule(static)
        for (int i = 0; i < LEN_1D/2; i++) {
            int j0 = 2 * i;
            a[j0] = b[i] + c[i] * d[i];
            a[j0 + 1] = b[i] + d[i] * e[i];
        }
        /* Restore j to the value the sequential loop left behind. */
        if (LEN_1D/2 > 0) j = 2 * (LEN_1D/2) - 1;
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s127)
