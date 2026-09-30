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
    real_t *tu = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    real_t *tv = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < R; nl++) {
        /* Phase 1: gather the increment for u's owned slot (old u, old v). */
        for (long i = 1; i < LEN_1D; i++) {
            tu[i] = u[ju[i]] + v[kv[i]] * c[i];
        }
        /* Phase 2: commit u so that phase 3 sees the fully-updated array,
         * exactly as the original in-order loop would once it reached the
         * matching index. */
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] = tu[i];
        }
        /* Phase 3: gather the new v value from the now up-to-date u. */
        for (long i = 1; i < LEN_1D; i++) {
            tv[i] = u[ku[i]] * d[i] + c[i];
        }
        /* Phase 4: commit v. */
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = tv[i];
        }
        pb_mix(nl);
    }
    free(tu);
    free(tv);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
