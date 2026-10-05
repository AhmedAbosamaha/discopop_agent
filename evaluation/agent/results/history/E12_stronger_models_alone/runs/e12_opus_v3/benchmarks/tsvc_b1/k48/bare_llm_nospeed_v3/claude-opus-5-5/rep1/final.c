/* Kernel k48. */
#include "tsvc_b1/k48.h"
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

static real_t kernel_k48(void)
{
    /* Inspector: assign each iteration a wavefront level so that any two
     * iterations touching the same u/v element (at least one writing) are
     * in different levels, ordered as in the original loop. */
    long n = (long)LEN_1D;
    int *lvl = (int *)malloc((size_t)(n > 0 ? n : 1) * sizeof(int));
    int *wu = (int *)calloc((size_t)(n > 0 ? n : 1), sizeof(int));
    int *ru = (int *)calloc((size_t)(n > 0 ? n : 1), sizeof(int));
    int *wv = (int *)calloc((size_t)(n > 0 ? n : 1), sizeof(int));
    int *rv = (int *)calloc((size_t)(n > 0 ? n : 1), sizeof(int));
    int maxlev = 0;
    for (long i = 1; i < n; i++) {
        long x1 = (long)ju[i], x2 = (long)ku[i];
        long y1 = (long)kv[i], y2 = (long)jv[i];
        int L = 0;
        if (wu[x1] > L) L = wu[x1];
        if (ru[x1] > L) L = ru[x1];
        if (wu[x2] > L) L = wu[x2];
        if (wv[y1] > L) L = wv[y1];
        if (wv[y2] > L) L = wv[y2];
        if (rv[y2] > L) L = rv[y2];
        L += 1;
        lvl[i] = L;
        wu[x1] = L;
        if (ru[x2] < L) ru[x2] = L;
        if (rv[y1] < L) rv[y1] = L;
        wv[y2] = L;
        if (L > maxlev) maxlev = L;
    }
    free(wu); free(ru); free(wv); free(rv);

    long *start = (long *)calloc((size_t)maxlev + 2, sizeof(long));
    long *order = (long *)malloc((size_t)(n > 0 ? n : 1) * sizeof(long));
    for (long i = 1; i < n; i++) start[lvl[i] + 1]++;
    for (int l = 1; l <= maxlev; l++) start[l + 1] += start[l];
    {
        long *pos = (long *)malloc(((size_t)maxlev + 2) * sizeof(long));
        for (int l = 0; l <= maxlev + 1; l++) pos[l] = start[l];
        for (long i = 1; i < n; i++) order[pos[lvl[i]]++] = i;
        free(pos);
    }
    free(lvl);

    for (int nl = 0; nl < R; nl++) {
        for (int l = 1; l <= maxlev; l++) {
            long lo = start[l], hi = start[l + 1];
            #pragma omp parallel for schedule(static) shared(order) firstprivate(lo, hi)
            for (long p = lo; p < hi; p++) {
                long i = order[p];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        pb_mix(nl);
    }
    free(start);
    free(order);
    return (real_t)0;
}

PB_MAIN(kernel_k48)
