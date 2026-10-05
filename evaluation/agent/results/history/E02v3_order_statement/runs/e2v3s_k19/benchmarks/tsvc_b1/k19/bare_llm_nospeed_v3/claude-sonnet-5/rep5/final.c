/* Kernel k19. */
#include "tsvc_b1/k19.h"

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

static real_t kernel_k19(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* Each iteration i only ever touches its own exclusive pair of slots
         * ju[i] (in u) and jv[i] (in v): ju/jv are permutations of the index
         * range, and the reads via ku[i]/kv[i] resolve to those very same
         * slots, so the only "reuse" of a location is the write-then-read of
         * the SAME i that the statement order below already preserves. No
         * value written by one i is ever read by a different i, so the
         * iterations are independent and can run in any order/interleaving.
         */
        #pragma omp parallel for shared(u, v, c, d, ju, jv, ku, kv)
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k19)
