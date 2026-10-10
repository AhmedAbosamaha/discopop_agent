#include "data.h"
#include <stdlib.h>

static inline long k53_lmax(long x, long y) { return x > y ? x : y; }

real_t kernel_k53(void)
{
    const long n = LEN_1D - 1;          /* iterations i = 1 .. LEN_1D-1 */

    /* ---- inspector: range of the indirect indices ------------------- */
    long maxidx = 0;
    #pragma omp parallel for shared(ju, jv, ku, kv) reduction(max:maxidx)
    for (long i = 1; i < LEN_1D; i++) {
        long m = ju[i];
        if ((long)jv[i] > m) m = jv[i];
        if ((long)ku[i] > m) m = ku[i];
        if ((long)kv[i] > m) m = kv[i];
        if (m > maxidx) maxidx = m;
    }
    const long range = maxidx + 1;

    int  *lwu   = (int *)malloc((size_t)range * sizeof(int));   /* last write level, u */
    int  *lru   = (int *)malloc((size_t)range * sizeof(int));   /* last read  level, u */
    int  *lwv   = (int *)malloc((size_t)range * sizeof(int));   /* last write level, v */
    int  *lrv   = (int *)malloc((size_t)range * sizeof(int));   /* last read  level, v */
    int  *level = (int *)malloc((size_t)(n > 0 ? n : 1) * sizeof(int));
    long *start = (long *)malloc((size_t)(n + 2) * sizeof(long));
    long *order = (long *)malloc((size_t)(n > 0 ? n : 1) * sizeof(long));

    if (!lwu || !lru || !lwv || !lrv || !level || !start || !order) {
        /* allocation failure: fall back to the original sequential loop */
        free(lwu); free(lru); free(lwv); free(lrv);
        free(level); free(start); free(order);
        for (int nl = 0; nl < iterations; nl++) {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            dummy(a, b, c, d, e);
        }
        return (real_t)0;
    }

    /* ---- inspector: dependence levels (sequential, O(n), once) ------ */
    for (long k = 0; k < range; k++) { lwu[k] = 0; lru[k] = 0; lwv[k] = 0; lrv[k] = 0; }

    int nlevels = 0;
    for (long i = 1; i < LEN_1D; i++) {
        const int a_ju = ju[i], a_jv = jv[i], a_ku = ku[i], a_kv = kv[i];
        long L = lwv[a_kv];                                  /* read  v[kv[i]] */
        L = k53_lmax(L, k53_lmax(lwu[a_ju], lru[a_ju]));     /* RMW   u[ju[i]] */
        L = k53_lmax(L, lwu[a_ku]);                          /* read  u[ku[i]] */
        L = k53_lmax(L, k53_lmax(lwv[a_jv], lrv[a_jv]));     /* write v[jv[i]] */
        L += 1;
        const int lv = (int)L;
        level[i - 1] = lv;
        if (lrv[a_kv] < lv) lrv[a_kv] = lv;
        lwu[a_ju] = lv;
        if (lru[a_ku] < lv) lru[a_ku] = lv;
        lwv[a_jv] = lv;
        if (lv > nlevels) nlevels = lv;
    }

    /* ---- counting sort of iterations by level ----------------------- */
    for (long L = 0; L <= nlevels + 1 && L <= n + 1; L++) start[L] = 0;
    for (long k = 0; k < n; k++) start[level[k] + 1]++;
    for (long L = 1; L <= nlevels + 1; L++) start[L] += start[L - 1];
    /* start[L] .. start[L+1]-1 now holds the slots of level L (levels 1..nlevels) */
    for (long k = 0; k < n; k++) order[start[level[k]]++] = k + 1;
    /* restore start[] to bucket beginnings */
    for (long L = nlevels; L >= 1; L--) start[L] = start[L - 1];
    start[0] = 0;

    free(lwu); free(lru); free(lwv); free(lrv); free(level);

    /* ---- executor ---------------------------------------------------- */
    for (int nl = 0; nl < iterations; nl++) {
        for (int L = 1; L <= nlevels; L++) {
            long lo = start[L];
            long hi = start[L + 1];
            long cnt = hi - lo;
            #pragma omp parallel for if(cnt > 32) \
                shared(order, u, v, c, d, ju, jv, ku, kv) firstprivate(lo, hi)
            for (long j = lo; j < hi; j++) {
                const long i = order[j];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(start); free(order);
    return (real_t)0;
}
