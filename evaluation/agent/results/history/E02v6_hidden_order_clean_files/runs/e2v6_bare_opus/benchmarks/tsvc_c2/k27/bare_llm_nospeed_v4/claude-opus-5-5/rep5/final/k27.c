#include <stdlib.h>
#include "data.h"

static inline int k27_imax(int x, int y) { return x > y ? x : y; }

real_t kernel_k27(void)
{
    const long n = LEN_1D;

    /* ---- inspector: size of tracking tables ---- */
    int maxIdx = 0;
    for (long i = 1; i < n; i++) {
        maxIdx = k27_imax(maxIdx, ju[i]);
        maxIdx = k27_imax(maxIdx, jv[i]);
        maxIdx = k27_imax(maxIdx, jw[i]);
        maxIdx = k27_imax(maxIdx, ku[i]);
        maxIdx = k27_imax(maxIdx, kv[i]);
        maxIdx = k27_imax(maxIdx, kw[i]);
    }
    long m = (long)maxIdx + 1;

    int *wrU = (int *)malloc((size_t)m * sizeof(int));
    int *rdU = (int *)malloc((size_t)m * sizeof(int));
    int *wrV = (int *)malloc((size_t)m * sizeof(int));
    int *rdV = (int *)malloc((size_t)m * sizeof(int));
    int *wrW = (int *)malloc((size_t)m * sizeof(int));
    int *rdW = (int *)malloc((size_t)m * sizeof(int));
    for (long x = 0; x < m; x++) {
        wrU[x] = -1; rdU[x] = -1;
        wrV[x] = -1; rdV[x] = -1;
        wrW[x] = -1; rdW[x] = -1;
    }

    /* ---- inspector: assign each iteration a wavefront level ---- */
    int *lev = (int *)malloc((size_t)n * sizeof(int));
    int nlev = 0;
    for (long i = 1; i < n; i++) {
        int pu = ju[i], qw = kw[i], qu = ku[i];
        int pv = jv[i], qv = kv[i], pw = jw[i];
        int L = 0;
        /* reads: w[qw], u[pu], u[qu], v[qv]  (must follow last writes) */
        L = k27_imax(L, wrW[qw] + 1);
        L = k27_imax(L, wrU[pu] + 1);
        L = k27_imax(L, wrU[qu] + 1);
        L = k27_imax(L, wrV[qv] + 1);
        /* writes: u[pu], v[pv], w[pw]  (must follow last writes and reads) */
        L = k27_imax(L, rdU[pu] + 1);
        L = k27_imax(L, wrV[pv] + 1);
        L = k27_imax(L, rdV[pv] + 1);
        L = k27_imax(L, wrW[pw] + 1);
        L = k27_imax(L, rdW[pw] + 1);
        lev[i] = L;
        rdW[qw] = k27_imax(rdW[qw], L);
        rdU[pu] = k27_imax(rdU[pu], L);
        rdU[qu] = k27_imax(rdU[qu], L);
        rdV[qv] = k27_imax(rdV[qv], L);
        wrU[pu] = L;
        wrV[pv] = L;
        wrW[pw] = L;
        if (L + 1 > nlev) nlev = L + 1;
    }
    free(wrU); free(rdU); free(wrV); free(rdV); free(wrW); free(rdW);

    /* ---- bucket iterations by level (counting sort, stable) ---- */
    long *start = (long *)calloc((size_t)nlev + 1, sizeof(long));
    long *order = (long *)malloc((size_t)n * sizeof(long));
    for (long i = 1; i < n; i++) start[lev[i] + 1]++;
    for (int L = 0; L < nlev; L++) start[L + 1] += start[L];
    {
        long *pos = (long *)malloc((size_t)(nlev > 0 ? nlev : 1) * sizeof(long));
        for (int L = 0; L < nlev; L++) pos[L] = start[L];
        for (long i = 1; i < n; i++) order[pos[lev[i]]++] = i;
        free(pos);
    }
    free(lev);

    /* ---- executor ---- */
    for (int nl = 0; nl < iterations; nl++) {
        for (int L = 0; L < nlev; L++) {
            long lo = start[L];
            long hi = start[L + 1];
            #pragma omp parallel for schedule(static) shared(order)
            for (long k = lo; k < hi; k++) {
                long i = order[k];
                u[ju[i]] += w[kw[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
                w[jw[i]] = v[kv[i]] * e[i] + d[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(start);
    free(order);
    return (real_t)0;
}
