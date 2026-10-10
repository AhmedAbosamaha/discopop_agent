#include "data.h"
#include <stdlib.h>

/* Minimum number of iterations in a level before it is worth a parallel
   region; consecutive smaller levels are executed as one serial chunk
   (in level order, which respects every dependence). */
#define K53_PAR_MIN 16

real_t kernel_k53(void)
{
    const long n = LEN_1D;

    /* ---------------- inspector (runs once; indices never change) ------- */
    long maxidx = 0;
    for (long i = 1; i < n; i++) {
        if ((long)ju[i] > maxidx) maxidx = ju[i];
        if ((long)jv[i] > maxidx) maxidx = jv[i];
        if ((long)ku[i] > maxidx) maxidx = ku[i];
        if ((long)kv[i] > maxidx) maxidx = kv[i];
    }
    const long m = maxidx + 1;

    long *lwu = (long *)calloc((size_t)m, sizeof(long)); /* last write level of u[loc] */
    long *lru = (long *)calloc((size_t)m, sizeof(long)); /* last read  level of u[loc] */
    long *lwv = (long *)calloc((size_t)m, sizeof(long)); /* last write level of v[loc] */
    long *lrv = (long *)calloc((size_t)m, sizeof(long)); /* last read  level of v[loc] */
    long *level = (long *)malloc((size_t)(n > 0 ? n : 1) * sizeof(long));

    long nlev = 0;
    for (long i = 1; i < n; i++) {
        const long a1 = ju[i];   /* u write (read-modify-write) */
        const long a2 = ku[i];   /* u read */
        const long b1 = jv[i];   /* v write */
        const long b2 = kv[i];   /* v read */

        long L = lwu[a2];                 /* RAW on u[ku[i]] */
        if (lwu[a1] > L) L = lwu[a1];     /* RAW/WAW on u[ju[i]] */
        if (lru[a1] > L) L = lru[a1];     /* WAR on u[ju[i]] */
        if (lwv[b2] > L) L = lwv[b2];     /* RAW on v[kv[i]] */
        if (lwv[b1] > L) L = lwv[b1];     /* WAW on v[jv[i]] */
        if (lrv[b1] > L) L = lrv[b1];     /* WAR on v[jv[i]] */
        L += 1;
        level[i] = L;

        if (L > lru[a2]) lru[a2] = L;
        lwu[a1] = L;
        lru[a1] = L;
        if (L > lrv[b2]) lrv[b2] = L;
        lwv[b1] = L;
        if (L > nlev) nlev = L;
    }
    free(lwu);
    free(lru);
    free(lwv);
    free(lrv);

    /* stable bucket sort of iterations by level */
    long *cnt   = (long *)calloc((size_t)(nlev + 2), sizeof(long));
    long *start = (long *)calloc((size_t)(nlev + 2), sizeof(long));
    long *order = (long *)malloc((size_t)(n > 0 ? n : 1) * sizeof(long));
    for (long i = 1; i < n; i++) cnt[level[i]]++;
    start[1] = 0;
    for (long l = 1; l <= nlev; l++) start[l + 1] = start[l] + cnt[l];
    {
        long *pos = (long *)malloc((size_t)(nlev + 2) * sizeof(long));
        for (long l = 1; l <= nlev + 1; l++) pos[l] = start[l];
        for (long i = 1; i < n; i++) order[pos[level[i]]++] = i;
        free(pos);
    }
    free(level);

    /* ---------------- executor ---------------- */
    for (int nl = 0; nl < iterations; nl++) {
        long lev = 1;
        while (lev <= nlev) {
            if (cnt[lev] >= K53_PAR_MIN) {
                long ks = start[lev];
                long ke = start[lev + 1];
#pragma omp parallel for shared(order, u, v, c, d, ju, jv, ku, kv) firstprivate(ks, ke)
                for (long k = ks; k < ke; k++) {
                    const long i = order[k];
                    u[ju[i]] += v[kv[i]] * c[i];
                    v[jv[i]] = u[ku[i]] * d[i] + c[i];
                }
                lev++;
            } else {
                long lev2 = lev;
                while (lev2 <= nlev && cnt[lev2] < K53_PAR_MIN) lev2++;
                long ks = start[lev];
                long ke = start[lev2];
                for (long k = ks; k < ke; k++) {
                    const long i = order[k];
                    u[ju[i]] += v[kv[i]] * c[i];
                    v[jv[i]] = u[ku[i]] * d[i] + c[i];
                }
                lev = lev2;
            }
        }
        dummy(a, b, c, d, e);
    }

    free(cnt);
    free(start);
    free(order);
    return (real_t)0;
}
