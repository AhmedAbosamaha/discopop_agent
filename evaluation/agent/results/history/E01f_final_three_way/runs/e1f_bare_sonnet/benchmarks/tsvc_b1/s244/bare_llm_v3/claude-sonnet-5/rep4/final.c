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
        /* Original body, for each i: a[i] = b[i]+c[i]*d[i]; b[i] = c[i]+b[i];
         * a[i+1] = b[i] + a[i+1]*d[i]  (b[i] here is the just-updated value).
         * The third statement's write to a[i+1] is a dead store for every i
         * except the very last iteration (i == LEN_1D-2): the next
         * iteration's first statement, a[i+1] = b[i+1]+c[i+1]*d[i+1],
         * overwrites it before it is ever read. So the only true
         * cross-iteration dependence is that single last write, which only
         * needs the final value of b[LEN_1D-2] and the old a[LEN_1D-1] -
         * both available once the loop below has finished. With that write
         * pulled out, each iteration i only reads/writes index i of a and
         * b (and reads index i of c, d), so the remaining loop body is
         * independent across i and can run in parallel in any order/
         * schedule.
         */
        #pragma omp parallel for shared(a, b, c, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            real_t b_old = b[i];           /* old b[i], read before this iteration's update */
            a[i] = b_old + c[i] * d[i];
            b[i] = c[i] + b_old;
        }
        if (LEN_1D > 1) {
            a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d[LEN_1D-2];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_s244)
