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
    real_t *v_new = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    real_t *vsrc  = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < R; nl++) {
        /* Stage 1: the value line 20 would produce depends only on u
         * (still in its pre-pass state here), d and c -- never on v --
         * so every i is independent regardless of order. */
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            v_new[i] = u[ku[i]] * d[i] + c[i];
        }

        /* Stage 2: cheap bookkeeping-only replay, in the original order,
         * of exactly what v[kv[i]] held right before this i's own commit
         * (i.e. after commits from i' < i only, same as the fused loop
         * used to guarantee), then commit the precomputed new value.
         * No heavy arithmetic here, so this stays a plain O(LEN_1D) pass. */
        #pragma omp parallel for shared(v_new,vsrc) 
        for (long i = 1; i < LEN_1D; i++) {
            vsrc[i] = v[kv[i]];
            v[jv[i]] = v_new[i];
        }

        /* Stage 3: apply the accumulation using the values captured at
         * the right logical time above -- independent across i. */
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += vsrc[i] * c[i];
        }

        pb_mix(nl);
    }

    free(v_new);
    free(vsrc);

    return (real_t)0;
}

PB_MAIN(kernel_k19)
