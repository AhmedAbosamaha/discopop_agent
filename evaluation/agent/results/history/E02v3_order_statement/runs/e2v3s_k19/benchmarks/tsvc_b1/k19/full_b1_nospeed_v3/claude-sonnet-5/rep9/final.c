/* Kernel k19. */
#include "tsvc_b1/k19.h"
#include <stdlib.h>

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
    /* u[ku[i]] is never written by this loop (only u[ju[i]] is), so the
     * right-hand side of the v-update below does not depend on anything
     * produced during the i-loop: it can be computed for every i up front,
     * independently. The value that line 19 originally needed from v is
     * captured, in ascending i order, before the corresponding v write is
     * applied -- this preserves exactly which earlier write (if any) each
     * read observes. Once that value is captured, the accumulation into u
     * is order-independent (a plain sum) and can run in any order. */
    real_t *k19_rhs = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    real_t *k19_vseen = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        #pragma omp parallel for shared(k19_rhs) 
        for (long i = 1; i < LEN_1D; i++) {
            k19_rhs[i] = u[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            k19_vseen[i] = v[kv[i]];
            v[jv[i]] = k19_rhs[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += k19_vseen[i] * c[i];
        }
        pb_mix(nl);
    }

    free(k19_rhs);
    free(k19_vseen);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
