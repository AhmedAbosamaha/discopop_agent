/* Kernel k48. */
#include "tsvc_b1/k48.h"

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

static real_t kernel_k48(void)
{
    for (int nl = 0; nl < R; nl++) {
        /* The i-loop looks sequential to a static compiler because u and v are
         * touched through the indirect indices ju/kv/jv/ku, which it cannot
         * prove are collision-free across iterations.  At run time they are:
         * each iteration's u-slot (ju[i]) and v-slot (jv[i]) belongs to that
         * iteration alone, so no two iterations ever write - or write/read -
         * the same element of u or the same element of v.  The one real reuse
         * is u[ku[i]] being read right after u[ju[i]] was written, and that
         * reuse is confined to the SAME iteration i (a thread runs both of
         * its own statements in program order), so it carries no dependence
         * between iterations.  That makes the loop iterations independent as
         * written; nothing needs to be split into separate passes or snapshot
         * buffers.  u, v, c, d and the index arrays are all shared: c, d, ju,
         * jv, ku, kv are read-only in this loop, and u/v are shared because
         * each iteration's writes/reads land on elements no other iteration
         * touches. i is the loop variable and is private by construction.
         */
        #pragma omp parallel for default(none) shared(u, v, c, d, ju, jv, ku, kv) schedule(static)
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        pb_mix(nl);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k48)
