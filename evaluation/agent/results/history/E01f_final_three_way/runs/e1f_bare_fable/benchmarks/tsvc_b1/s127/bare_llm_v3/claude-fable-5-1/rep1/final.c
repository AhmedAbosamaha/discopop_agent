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
        /* j is an induction variable: j == 2*i and 2*i+1 inside iteration i.
         * Computed in closed form so iterations are independent; a[2i], a[2i+1]
         * are disjoint across i and b,c,d,e are read-only here. */
#pragma omp parallel for default(none) shared(a, b, c, d, e) schedule(static)
        for (int i = 0; i < LEN_1D/2; i++) {
            int j0 = 2 * i;
            a[j0] = b[i] + c[i] * d[i];
            a[j0 + 1] = b[i] + d[i] * e[i];
        }
        /* final value of the original induction variable (not read afterwards) */
        j = 2 * (LEN_1D/2) - 1;
        (void)j;
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s127)
