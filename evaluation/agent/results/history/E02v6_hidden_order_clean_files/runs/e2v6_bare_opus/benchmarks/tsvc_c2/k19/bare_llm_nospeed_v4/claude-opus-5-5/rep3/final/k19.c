#include <stdlib.h>
#include "data.h"

static int imax4(int a1, int a2, int a3, int a4)
{
    int m = a1;
    if (a2 > m) m = a2;
    if (a3 > m) m = a3;
    if (a4 > m) m = a4;
    return m;
}

real_t kernel_k19(void)
{
    /* ---- inspector: wavefront levels of the indirect recurrence ---- */
    long maxidx = 0;
    for (long i = 1; i < LEN_1D; i++) {
        if (ju[i] > maxidx) maxidx = ju[i];
        if (jv[i] > maxidx) maxidx = jv[i];
        if (ku[i] > maxidx) maxidx = ku[i];
        if (kv[i] > maxidx) maxidx = kv[i];
    }
    long m = maxidx + 1;

    int *lw_u = (int *)calloc((size_t)m, sizeof(int)); /* level of last write */
    int *la_u = (int *)calloc((size_t)m, sizeof(int)); /* max level of any access */
    int *lw_v = (int *)calloc((size_t)m, sizeof(int));
    int *la_v = (int *)calloc((size_t)m, sizeof(int));
    int *lev = (int *)malloc((size_t)LEN_1D * sizeof(int));
    int *order = (int *)malloc((size_t)LEN_1D * sizeof(int));

    if (!lw_u || !la_u || !lw_v || !la_v || !lev || !order) {
        free(lw_u); free(la_u); free(lw_v); free(la_v); free(lev); free(order);
        for (int nl = 0; nl < iterations; nl++) {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            dummy(a, b, c, d, e);
        }
        return (real_t)0;
    }

    int nlev = 0;
    for (long i = 1; i < LEN_1D; i++) {
        int a1 = ju[i], a2 = ku[i], b1 = kv[i], b2 = jv[i];
        /* reads: v[b1], u[a1], u[a2]; writes: u[a1], v[b2] */
        int L = 1 + imax4(lw_v[b1], la_u[a1], lw_u[a2], la_v[b2]);
        lev[i] = L;
        if (L > nlev) nlev = L;
        if (la_v[b1] < L) la_v[b1] = L;
        lw_u[a1] = L;
        if (la_u[a1] < L) la_u[a1] = L;
        if (la_u[a2] < L) la_u[a2] = L;
        lw_v[b2] = L;
        if (la_v[b2] < L) la_v[b2] = L;
    }
    free(lw_u); free(la_u); free(lw_v); free(la_v);

    /* counting sort of iterations by level (levels 1..nlev) */
    long *start = (long *)calloc((size_t)nlev + 2, sizeof(long));
    if (!start) {
        free(lev); free(order);
        for (int nl = 0; nl < iterations; nl++) {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            dummy(a, b, c, d, e);
        }
        return (real_t)0;
    }
    for (long i = 1; i < LEN_1D; i++)
        start[lev[i] + 1]++;
    for (int L = 1; L <= nlev; L++)
        start[L + 1] += start[L];
    {
        long *pos = (long *)malloc((size_t)(nlev + 2) * sizeof(long));
        if (pos) {
            for (int L = 0; L <= nlev + 1; L++) pos[L] = start[L];
            for (long i = 1; i < LEN_1D; i++)
                order[pos[lev[i]]++] = (int)i;
            free(pos);
        } else {
            /* fallback: fill using start as cursor, then restore */
            for (long i = 1; i < LEN_1D; i++)
                order[start[lev[i]]++] = (int)i;
            for (int L = nlev; L >= 1; L--)
                start[L] = start[L - 1];
            start[0] = 0;
            start[1] = 0;
        }
    }
    free(lev);

    /* ---- executor ---- */
    for (int nl = 0; nl < iterations; nl++) {
        for (int L = 1; L <= nlev; L++) {
            long lo = start[L], hi = start[L + 1];
            #pragma omp parallel for default(none) shared(u, v, c, d, ju, jv, ku, kv, order) firstprivate(lo, hi) schedule(static)
            for (long k = lo; k < hi; k++) {
                long i = order[k];
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
