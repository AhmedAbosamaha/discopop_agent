#include <stdlib.h>
#include "data.h"

static int imax2(int x, int y) { return x > y ? x : y; }

real_t kernel_k48(void)
{
    const long n = LEN_1D;

    /* ---- inspector: dependence levels (index arrays never change) ---- */
    long lo = 0, hi = 0;
    if (n > 1) {
        lo = ju[1]; hi = ju[1];
    }
    for (long i = 1; i < n; i++) {
        long t0 = ju[i], t1 = jv[i], t2 = ku[i], t3 = kv[i];
        if (t0 < lo) lo = t0; if (t0 > hi) hi = t0;
        if (t1 < lo) lo = t1; if (t1 > hi) hi = t1;
        if (t2 < lo) lo = t2; if (t2 > hi) hi = t2;
        if (t3 < lo) lo = t3; if (t3 > hi) hi = t3;
    }
    long range = hi - lo + 1;

    int *wU = (int *)malloc((size_t)range * sizeof(int));
    int *rU = (int *)malloc((size_t)range * sizeof(int));
    int *wV = (int *)malloc((size_t)range * sizeof(int));
    int *rV = (int *)malloc((size_t)range * sizeof(int));
    int *lev = (int *)malloc((size_t)n * sizeof(int));
    long *order = (long *)malloc((size_t)n * sizeof(long));

    for (long k = 0; k < range; k++) {
        wU[k] = -1; rU[k] = -1; wV[k] = -1; rV[k] = -1;
    }

    int maxlev = -1;
    for (long i = 1; i < n; i++) {
        long xju = ju[i] - lo, xjv = jv[i] - lo, xku = ku[i] - lo, xkv = kv[i] - lo;
        int L = 0;
        /* stmt 1: read v[kv], read+write u[ju] */
        L = imax2(L, wV[xkv] + 1);
        L = imax2(L, wU[xju] + 1);
        L = imax2(L, rU[xju] + 1);
        /* stmt 2: read u[ku], write v[jv] */
        L = imax2(L, wU[xku] + 1);
        L = imax2(L, wV[xjv] + 1);
        L = imax2(L, rV[xjv] + 1);
        lev[i] = L;
        wU[xju] = L;
        rU[xju] = imax2(rU[xju], L);
        rU[xku] = imax2(rU[xku], L);
        rV[xkv] = imax2(rV[xkv], L);
        wV[xjv] = L;
        if (L > maxlev) maxlev = L;
    }

    int nlev = maxlev + 1;
    long *lstart = (long *)malloc((size_t)(nlev + 1) * sizeof(long));
    for (int l = 0; l <= nlev; l++) lstart[l] = 0;
    for (long i = 1; i < n; i++) lstart[lev[i] + 1]++;
    for (int l = 0; l < nlev; l++) lstart[l + 1] += lstart[l];
    {
        long *pos = (long *)malloc((size_t)(nlev + 1) * sizeof(long));
        for (int l = 0; l <= nlev; l++) pos[l] = lstart[l];
        for (long i = 1; i < n; i++) order[pos[lev[i]]++] = i;
        free(pos);
    }

    /* ---- executor ---- */
    for (int nl = 0; nl < iterations; nl++) {
        for (int l = 0; l < nlev; l++) {
            long pb = lstart[l];
            long pe = lstart[l + 1];
            #pragma omp parallel for schedule(static) shared(u, v, ju, jv, ku, kv, c, d, order)
            for (long p = pb; p < pe; p++) {
                long i = order[p];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(wU); free(rU); free(wV); free(rV);
    free(lev); free(order); free(lstart);
    return (real_t)0;
}
