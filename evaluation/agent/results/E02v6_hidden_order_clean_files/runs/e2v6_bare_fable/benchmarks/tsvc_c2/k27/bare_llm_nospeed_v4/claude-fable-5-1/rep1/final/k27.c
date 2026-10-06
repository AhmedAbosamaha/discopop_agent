#include "data.h"
#include <stdlib.h>

real_t kernel_k27(void)
{
    const long n = LEN_1D;

    /* ------------------------------------------------------------------
     * Inspector: the index arrays never change, so compute once a
     * wavefront level for every iteration i (1..n-1).  Each iteration
     *   reads  w[kw[i]], u[ku[i]], v[kv[i]]
     *   writes u[ju[i]] (read-modify-write), v[jv[i]], w[jw[i]]
     * level(i) must exceed the level of the last write to anything it
     * reads, and the level of the last write AND last read of anything it
     * writes.  Then all iterations of one level touch pairwise
     * non-conflicting locations, and every dependence (RAW, WAR, WAW) runs
     * from a lower level to a higher one, so executing levels in order and
     * each level in any order reproduces the serial result exactly.
     * ------------------------------------------------------------------ */
    int *lwu = (int *)malloc(sizeof(int) * (size_t)n);
    int *lru = (int *)malloc(sizeof(int) * (size_t)n);
    int *lwv = (int *)malloc(sizeof(int) * (size_t)n);
    int *lrv = (int *)malloc(sizeof(int) * (size_t)n);
    int *lww = (int *)malloc(sizeof(int) * (size_t)n);
    int *lrw = (int *)malloc(sizeof(int) * (size_t)n);
    int *lev = (int *)malloc(sizeof(int) * (size_t)n);

    for (long x = 0; x < n; x++) {
        lwu[x] = -1; lru[x] = -1;
        lwv[x] = -1; lrv[x] = -1;
        lww[x] = -1; lrw[x] = -1;
    }

    int nlev = 0;
    lev[0] = 0;
    for (long i = 1; i < n; i++) {
        const int iju = ju[i], iku = ku[i];
        const int ijv = jv[i], ikv = kv[i];
        const int ijw = jw[i], ikw = kw[i];
        int L = -1;
        /* u[ju[i]] is read and written */
        if (lwu[iju] > L) L = lwu[iju];
        if (lru[iju] > L) L = lru[iju];
        /* u[ku[i]] is read */
        if (lwu[iku] > L) L = lwu[iku];
        /* v[jv[i]] is written */
        if (lwv[ijv] > L) L = lwv[ijv];
        if (lrv[ijv] > L) L = lrv[ijv];
        /* v[kv[i]] is read */
        if (lwv[ikv] > L) L = lwv[ikv];
        /* w[jw[i]] is written */
        if (lww[ijw] > L) L = lww[ijw];
        if (lrw[ijw] > L) L = lrw[ijw];
        /* w[kw[i]] is read */
        if (lww[ikw] > L) L = lww[ikw];
        L += 1;
        lev[i] = L;
        if (L + 1 > nlev) nlev = L + 1;

        lwu[iju] = L;
        if (lru[iku] < L) lru[iku] = L;
        lwv[ijv] = L;
        if (lrv[ikv] < L) lrv[ikv] = L;
        lww[ijw] = L;
        if (lrw[ikw] < L) lrw[ikw] = L;
    }

    free(lwu); free(lru);
    free(lwv); free(lrv);
    free(lww); free(lrw);

    /* Bucket iterations by level (counting sort). */
    long *start = (long *)malloc(sizeof(long) * (size_t)(nlev + 1));
    long *fill  = (long *)malloc(sizeof(long) * (size_t)(nlev + 1));
    long *order = (long *)malloc(sizeof(long) * (size_t)n);

    for (int L = 0; L <= nlev; L++) start[L] = 0;
    for (long i = 1; i < n; i++) start[lev[i] + 1]++;
    for (int L = 0; L < nlev; L++) start[L + 1] += start[L];
    for (int L = 0; L <= nlev; L++) fill[L] = start[L];
    for (long i = 1; i < n; i++) order[fill[lev[i]]++] = i;

    free(fill);
    free(lev);

    /* ------------------------------------------------------------------
     * Executor: levels in order, each level's iterations in parallel.
     * Within a level no two iterations write the same element of u, v or
     * w, and no iteration reads an element another iteration of the same
     * level writes, so the body is race-free and order-independent.
     * ------------------------------------------------------------------ */
    for (int nl = 0; nl < iterations; nl++) {
        for (int L = 0; L < nlev; L++) {
            const long lo = start[L];
            const long hi = start[L + 1];
#pragma omp parallel for if(hi - lo >= 256) \
            shared(order, u, v, w, c, d, e, ju, jv, jw, ku, kv, kw) \
            firstprivate(lo, hi)
            for (long k = lo; k < hi; k++) {
                const long i = order[k];
                u[ju[i]] += w[kw[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
                w[jw[i]] = v[kv[i]] * e[i] + d[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(order);
    free(start);

    return (real_t)0;
}
