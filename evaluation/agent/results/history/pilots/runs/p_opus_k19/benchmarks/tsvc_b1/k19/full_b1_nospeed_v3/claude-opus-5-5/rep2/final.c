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
    /* Inspector: assign each iteration a wavefront level that respects every
     * RAW / WAR / WAW between iterations (index arrays never change). */
    long n = LEN_1D;
    long m = 1;
    for (long i = 1; i < n; i++) {
        long e1 = (long)ju[i], e2 = (long)ku[i], e3 = (long)kv[i], e4 = (long)jv[i];
        if (e1 + 1 > m) m = e1 + 1;
        if (e2 + 1 > m) m = e2 + 1;
        if (e3 + 1 > m) m = e3 + 1;
        if (e4 + 1 > m) m = e4 + 1;
    }
    int *lvl = (int *)malloc((size_t)n * sizeof(int));
    int *uw = (int *)calloc((size_t)m, sizeof(int));
    int *ur = (int *)calloc((size_t)m, sizeof(int));
    int *vw = (int *)calloc((size_t)m, sizeof(int));
    int *vr = (int *)calloc((size_t)m, sizeof(int));
    int maxl = 0;
    for (long i = 1; i < n; i++) {
        long eu = (long)ju[i], ek = (long)ku[i], er = (long)kv[i], ew = (long)jv[i];
        int L = 1;
        if (uw[eu] + 1 > L) L = uw[eu] + 1;
        if (ur[eu] + 1 > L) L = ur[eu] + 1;
        if (uw[ek] + 1 > L) L = uw[ek] + 1;
        if (vw[er] + 1 > L) L = vw[er] + 1;
        if (vw[ew] + 1 > L) L = vw[ew] + 1;
        if (vr[ew] + 1 > L) L = vr[ew] + 1;
        lvl[i] = L;
        if (L > maxl) maxl = L;
        uw[eu] = L;
        if (ur[eu] < L) ur[eu] = L;
        if (ur[ek] < L) ur[ek] = L;
        if (vr[er] < L) vr[er] = L;
        vw[ew] = L;
    }
    free(uw); free(ur); free(vw); free(vr);

    /* Stable counting sort of iterations by level. */
    long *start = (long *)calloc((size_t)maxl + 2, sizeof(long));
    long *order = (long *)malloc((size_t)(n > 1 ? n : 1) * sizeof(long));
    for (long i = 1; i < n; i++) start[lvl[i]]++;
    {
        long acc = 0;
        for (int l = 0; l <= maxl + 1; l++) { long t = start[l]; start[l] = acc; acc += t; }
    }
    {
        long *pos = (long *)malloc(((size_t)maxl + 2) * sizeof(long));
        for (int l = 0; l <= maxl + 1; l++) pos[l] = start[l];
        for (long i = 1; i < n; i++) order[pos[lvl[i]]++] = i;
        free(pos);
    }
    free(lvl);

    for (int nl = 0; nl < R; nl++) {
        for (int l = 1; l <= maxl; l++) {
            long lo = start[l];
            long hi = start[l + 1];
 #pragma omp parallel for firstprivate(lo,hi) shared(order) 
            for (long k = lo; k < hi; k++) {
                long i = order[k];
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

PB_MAIN(kernel_k19)
