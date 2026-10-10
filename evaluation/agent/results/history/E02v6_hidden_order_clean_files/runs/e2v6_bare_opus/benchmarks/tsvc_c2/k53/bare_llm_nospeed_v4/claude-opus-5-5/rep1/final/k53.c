#include <stdlib.h>
#include "data.h"

real_t kernel_k53(void)
{
    const long n = LEN_1D;

    /* size of the location-tracking tables (largest index used + 1) */
    long umax = 0, vmax = 0;
#pragma omp parallel for schedule(static) reduction(max:umax, vmax)
    for (long i = 1; i < n; i++) {
        long x = ju[i] > ku[i] ? ju[i] : ku[i];
        long y = jv[i] > kv[i] ? jv[i] : kv[i];
        if (x > umax) umax = x;
        if (y > vmax) vmax = y;
    }

    int *wu = (int *)calloc((size_t)umax + 1, sizeof(int)); /* level of last write to u[x] */
    int *ru = (int *)calloc((size_t)umax + 1, sizeof(int)); /* max level that read u[x]    */
    int *wv = (int *)calloc((size_t)vmax + 1, sizeof(int));
    int *rv = (int *)calloc((size_t)vmax + 1, sizeof(int));
    int *lev = (int *)malloc((size_t)n * sizeof(int));
    int nlev = 0;

    /* inspector: assign each iteration the earliest level respecting all
       RAW / WAR / WAW dependences through u and v (sequential, O(n)) */
    for (long i = 1; i < n; i++) {
        long a1 = kv[i], a2 = ju[i], a3 = ku[i], a4 = jv[i];
        int L = 1, t;
        t = wv[a1] + 1; if (t > L) L = t;           /* read  v[kv[i]] */
        t = wu[a2] + 1; if (t > L) L = t;           /* r/w   u[ju[i]] */
        t = ru[a2] + 1; if (t > L) L = t;
        t = wu[a3] + 1; if (t > L) L = t;           /* read  u[ku[i]] */
        t = wv[a4] + 1; if (t > L) L = t;           /* write v[jv[i]] */
        t = rv[a4] + 1; if (t > L) L = t;
        lev[i] = L;
        if (L > nlev) nlev = L;
        if (rv[a1] < L) rv[a1] = L;
        if (ru[a2] < L) ru[a2] = L;
        if (ru[a3] < L) ru[a3] = L;
        wu[a2] = L;
        wv[a4] = L;
    }
    free(wu); free(ru); free(wv); free(rv);

    /* counting sort of iterations by level */
    long *start = (long *)calloc((size_t)nlev + 2, sizeof(long));
    long *order = (long *)malloc((size_t)(n > 1 ? n - 1 : 1) * sizeof(long));
    for (long i = 1; i < n; i++)
        start[lev[i] + 1]++;
    for (int l = 1; l <= nlev; l++)
        start[l + 1] += start[l];
    {
        long *pos = (long *)malloc(((size_t)nlev + 2) * sizeof(long));
        for (int l = 0; l <= nlev + 1; l++)
            pos[l] = start[l];
        for (long i = 1; i < n; i++)
            order[pos[lev[i]]++] = i;
        free(pos);
    }
    free(lev);

    for (int nl = 0; nl < iterations; nl++) {
        for (int l = 1; l <= nlev; l++) {
            const long lo = start[l];
            const long hi = start[l + 1];
#pragma omp parallel for schedule(static) shared(order)
            for (long p = lo; p < hi; p++) {
                long i = order[p];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(start);
    free(order);
    return (real_t)0;
}
