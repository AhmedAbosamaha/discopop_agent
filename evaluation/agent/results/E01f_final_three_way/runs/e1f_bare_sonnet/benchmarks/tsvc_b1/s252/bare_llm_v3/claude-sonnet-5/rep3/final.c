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
    for (int nl = 0; nl < R; nl++) {
        /* Original recurrence: t starts at 0 each repetition, and each
         * iteration i computes s = b[i]*c[i], writes a[i] = s + t, then
         * carries t = s into iteration i+1. So the value iteration i reads
         * as "t" is exactly the s computed by iteration i-1 (0 for i==0).
         * That value is a pure function of b[i-1]*c[i-1], already-shared
         * read-only data, so instead of carrying it forward we recompute it
         * locally in each iteration: a[i] = b[i]*c[i] + (i>0 ? b[i-1]*c[i-1] : 0).
         * This removes the loop-carried dependence entirely (no value is
         * dropped, it is just re-derived from data every iteration can see),
         * so iterations can run in any order/partition.
         * a, b, c are shared arrays: each iteration reads b[i], c[i] and
         * (for i>0) b[i-1], c[i-1], and writes only its own a[i] -- disjoint
         * writes, no races. LEN_1D is a compile-time constant (loop bound),
         * no sharing clause needed for it.
         */
        #pragma omp parallel for default(none) shared(a, b, c)
        for (int i = 0; i < LEN_1D; i++) {
            real_t s_i = b[i] * c[i];
            real_t t_prev = (i == 0) ? (real_t)0. : b[i - 1] * c[i - 1];
            a[i] = s_i + t_prev;
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s252)
