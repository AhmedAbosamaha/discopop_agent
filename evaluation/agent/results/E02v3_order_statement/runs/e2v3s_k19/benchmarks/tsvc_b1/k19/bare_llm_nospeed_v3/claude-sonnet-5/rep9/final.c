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
        /* Each iteration i only ever touches element i of u/v (the index
         * arrays are the identity permutation): statement 1 folds the OLD
         * v[i] (left over from the previous repetition) into u[i], and
         * statement 2 immediately consumes the freshly-updated u[i] to
         * overwrite v[i]. That value flow is entirely local to iteration i;
         * no iteration reads a u/v element another iteration of this same
         * loop writes. What looked like a cross-iteration dependence via
         * ju/jv/ku/kv is really just the same pair of locations addressed
         * twice within one iteration, so the iterations are independent of
         * one another and can run in any order or interleaving.
         * c and d are read-only here (pb_mix only updates them between
         * repetitions of nl), and ju/jv/ku/kv are read-only index tables. */
#pragma omp parallel for default(none) shared(u, v, c, d, ju, jv, ku, kv) schedule(static)
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k19)
