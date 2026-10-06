#include <stdlib.h>
#include "data.h"

real_t kernel_k48(void)
{
    const long n = LEN_1D;

    /* ---- inspector: done once, index arrays never change ---- */
    long maxidx = 0;
    for (long i = 1; i < n; i++) {
        if (ju[i] > maxidx) maxidx = ju[i];
        if (jv[i] > maxidx) maxidx = jv[i];
        if (ku[i] > maxidx) maxidx = ku[i];
        if (kv[i] > maxidx) maxidx = kv[i];
    }
    long m = maxidx + 1;

    int *wu = (int *)malloc((size_t)m * sizeof(int)); /* last write level on u[x] */
    int *ru = (int *)malloc((size_t)m * sizeof(int)); /* max read level on u[x]   */
    int *wv = (int *)malloc((size_t)m * sizeof(int));
    int *rv = (int *)malloc((size_t)m * sizeof(int));
    int *lev = (int *)malloc((size_t)n * sizeof(int));
    for (long x = 0; x < m; x++) { wu[x] = -1; ru[x] = -1; wv[x] = -1; rv[x] = -1; }

    int nlev = 0;
    for (long i = 1; i < n; i++) {
        long a1 = ju[i], a2 = ku[i], b1 = kv[i], b2 = jv[i];
        int L = -1;
        /* reads: u[ju], u[ku], v[kv]  -> after last writers */
        if (wu[a1] > L) L = wu[a1];
        if (wu[a2] > L) L = wu[a2];
        if (wv[b1] > L) L = wv[b1];
        /* writes: u[ju], v[jv] -> after last writers and readers */
        if (ru[a1] > L) L = ru[a1];
        if (wv[b2] > L) L = wv[b2];
        if (rv[b2] > L) L = rv[b2];
        L += 1;
        lev[i] = L;
        if (L + 1 > nlev) nlev = L + 1;
        if (ru[a1] < L) ru[a1] = L;
        if (ru[a2] < L) ru[a2] = L;
        if (rv[b1] < L) rv[b1] = L;
        wu[a1] = L;
        wv[b2] = L;
    }

    long *start = (long *)calloc((size_t)nlev + 2, sizeof(long));
    long *order = (long *)malloc((size_t)n * sizeof(long));
    for (long i = 1; i < n; i++) start[lev[i] + 1]++;
    for (int L = 0; L < nlev; L++) start[L + 1] += start[L];
    {
        long *pos = (long *)malloc(((size_t)nlev + 1) * sizeof(long));
        for (int L = 0; L <= nlev; L++) pos[L] = start[L];
        for (long i = 1; i < n; i++) order[pos[lev[i]]++] = i;
        free(pos);
    }

    /* ---- executor ---- */
    for (int nl = 0; nl < iterations; nl++) {
        for (int L = 0; L < nlev; L++) {
            long lo = start[L], hi = start[L + 1];
            #pragma omp parallel for default(none) shared(order, u, v, ju, jv, ku, kv, c, d) firstprivate(lo, hi) schedule(static) if(hi - lo >= 256)
            for (long p = lo; p < hi; p++) {
                long i = order[p];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(wu); free(ru); free(wv); free(rv);
    free(lev); free(start); free(order);
    return (real_t)0;
}
