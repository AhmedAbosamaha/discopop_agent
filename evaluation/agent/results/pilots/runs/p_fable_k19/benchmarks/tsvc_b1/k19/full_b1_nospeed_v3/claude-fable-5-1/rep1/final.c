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
    /* The index arrays never change, so the order in which v's elements are
     * stored and re-read is inspected once:
     *   src[i] : latest iteration i' < i that stored v[kv[i]]  (-1 if none)
     *   lw[j]  : last iteration that stores v[j]               (-1 if none) */
    long maxidx = 0;
    for (long i = 1; i < LEN_1D; i++) {
        if ((long)jv[i] > maxidx) maxidx = (long)jv[i];
        if ((long)kv[i] > maxidx) maxidx = (long)kv[i];
    }
    long   *lw  = (long *)malloc((size_t)(maxidx + 1) * sizeof(long));
    long   *src = (long *)malloc((size_t)LEN_1D * sizeof(long));
    real_t *w   = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (long j = 0; j <= maxidx; j++) {
        lw[j] = -1;
    }
    for (long i = 1; i < LEN_1D; i++) {
        src[i] = lw[kv[i]];
        lw[jv[i]] = i;
    }

    for (int nl = 0; nl < R; nl++) {
        /* value each iteration would store into v (u[ku[i]] is never written here) */
        #pragma omp parallel for shared(w) 
        for (long i = 1; i < LEN_1D; i++) {
            w[i] = u[ku[i]] * d[i] + c[i];
        }
        /* u update: the v value it saw is either an earlier iteration's store
         * or the value v held before this repetition */
        for (long i = 1; i < LEN_1D; i++) {
            real_t vi = (src[i] >= 0) ? w[src[i]] : v[kv[i]];
            u[ju[i]] += vi * c[i];
        }
        /* final v: only the last store to each element survives */
        #pragma omp parallel for shared(lw,w) 
        for (long i = 1; i < LEN_1D; i++) {
            if (lw[jv[i]] == i) {
                v[jv[i]] = w[i];
            }
        }
        pb_mix(nl);
    }
    free(w);
    free(src);
    free(lw);
    return (real_t)0;
}

PB_MAIN(kernel_k19)
