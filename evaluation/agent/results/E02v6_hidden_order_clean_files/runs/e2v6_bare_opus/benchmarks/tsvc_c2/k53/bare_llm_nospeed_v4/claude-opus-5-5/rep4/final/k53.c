#include <stdlib.h>
#include "data.h"

static int imax2(int x, int y) { return x > y ? x : y; }

real_t kernel_k53(void)
{
    const long n = LEN_1D;

    /* ---- inspector: dependence levels (index arrays are loop-invariant) ---- */
    long maxidx = 0;
    for (long i = 1; i < n; i++) {
        if (ju[i] > maxidx) maxidx = ju[i];
        if (jv[i] > maxidx) maxidx = jv[i];
        if (ku[i] > maxidx) maxidx = ku[i];
        if (kv[i] > maxidx) maxidx = kv[i];
    }
    long m = maxidx + 1;

    int *lwu = (int *)calloc((size_t)m, sizeof(int));
    int *lru = (int *)calloc((size_t)m, sizeof(int));
    int *lwv = (int *)calloc((size_t)m, sizeof(int));
    int *lrv = (int *)calloc((size_t)m, sizeof(int));
    int *lev = (int *)malloc((size_t)n * sizeof(int));
    long *ord = (long *)malloc((size_t)n * sizeof(long));

    int nlev = 0;
    for (long i = 1; i < n; i++) {
        int a1 = kv[i], b1 = ju[i], c1 = ku[i], d1 = jv[i];
        int L = 0;
        L = imax2(L, lwv[a1]);              /* read v[kv]         */
        L = imax2(L, lwu[b1]);              /* read/write u[ju]   */
        L = imax2(L, lru[b1]);
        L = imax2(L, lwu[c1]);              /* read u[ku]         */
        L = imax2(L, lwv[d1]);              /* write v[jv]        */
        L = imax2(L, lrv[d1]);
        L += 1;
        lev[i] = L;
        if (L > nlev) nlev = L;
        lrv[a1] = imax2(lrv[a1], L);
        lru[b1] = imax2(lru[b1], L);
        lwu[b1] = L;
        lru[c1] = imax2(lru[c1], L);
        lwv[d1] = L;
    }

    long *start = (long *)calloc((size_t)nlev + 2, sizeof(long));
    for (long i = 1; i < n; i++) start[lev[i] + 1]++;
    for (int l = 1; l <= nlev + 1; l++) start[l] += start[l - 1];
    /* start[l] = first slot of level l (levels 1..nlev), start[nlev+1] = total */
    {
        long *pos = (long *)malloc(((size_t)nlev + 2) * sizeof(long));
        for (int l = 0; l <= nlev + 1; l++) pos[l] = start[l];
        for (long i = 1; i < n; i++) ord[pos[lev[i]]++] = i;
        free(pos);
    }

    /* ---- executor ---- */
    for (int nl = 0; nl < iterations; nl++) {
        for (int l = 1; l <= nlev; l++) {
            long lo = start[l], hi = start[l + 1];
            #pragma omp parallel for schedule(static) default(none) shared(ord, u, v, ju, jv, ku, kv, c, d) firstprivate(lo, hi)
            for (long p = lo; p < hi; p++) {
                long i = ord[p];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(start);
    free(ord);
    free(lev);
    free(lrv);
    free(lwv);
    free(lru);
    free(lwu);
    return (real_t)0;
}
