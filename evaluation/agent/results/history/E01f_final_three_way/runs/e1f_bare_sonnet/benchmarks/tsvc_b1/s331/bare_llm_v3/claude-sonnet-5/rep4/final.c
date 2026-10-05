/* TSVC-2 loop s331, from TSVC-2 src/tsvc.c (sha256 456dd573b84b; University of Illinois licence,
 * see benchmarks/TSVC_2/license.txt). */
#include "tsvc_b1/s331.h"

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

static real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < R; nl++) {
        j = -1;
        /* Each iteration either leaves j untouched or sets it to i, and the
         * original loop keeps overwriting j so the largest qualifying i
         * wins (or -1 if none qualify). That is a max-reduction over the
         * per-iteration candidate i (or -1 when a[i] >= 0): no dependence
         * between iterations once expressed this way. a is read-only here
         * (shared), i is loop-private, j is the max-reduction accumulator
         * seeded at -1 as in the original. */
        #pragma omp parallel for shared(a) reduction(max:j)
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        chksum = (real_t) j;
        pb_mix(nl);
    }
    return j+1;
}

PB_MAIN(kernel_s331)
