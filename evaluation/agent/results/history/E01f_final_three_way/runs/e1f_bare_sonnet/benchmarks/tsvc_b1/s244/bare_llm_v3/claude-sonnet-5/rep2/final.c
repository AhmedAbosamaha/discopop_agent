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
        /* Statement 3's write to a[i+1] is overwritten by the next iteration's
         * statement 1 for every i < LEN_1D-2, so it only ever survives for the
         * very last index (i == LEN_1D-2 -> a[LEN_1D-1]). Pulling that single
         * surviving update out of the loop removes the only cross-iteration
         * dependence, leaving each remaining iteration touching only its own
         * a[i]/b[i]. */
        #pragma omp parallel for default(none) shared(a, b, c, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            real_t old_b = b[i];
            a[i] = old_b + c[i] * d[i];
            b[i] = c[i] + old_b;
        }
        if (LEN_1D > 1) {
            a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d[LEN_1D-2];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s244)
