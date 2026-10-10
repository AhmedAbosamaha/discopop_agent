#include <stdlib.h>
#include "data.h"

real_t kernel_k53(void)
{
    const long n = LEN_1D;

    /* ---- inspector: index arrays are invariant across nl ---- */
    long lo = 0, hi = 0;
    int first = 1;
    for (long i = 1; i < n; i++) {
        long idx[4] = { ju[i], jv[i], ku[i], kv[i] };
        for (int q = 0; q < 4; q++) {
            if (first) { lo = hi = idx[q]; first = 0; }
            if (idx[q] < lo) lo = idx[q];
            if (idx[q] > hi) hi = idx[q];
        }
    }
    long range = hi - lo + 1;
    if (range < 1) range = 1;

    int *uw = (int *)calloc((size_t)range, sizeof(int)); /* last write level on u */
    int *ur = (int *)calloc((size_t)range, sizeof(int)); /* max read level on u */
    int *vw = (int *)calloc((size_t)range, sizeof(int));
    int *vr = (int *)calloc((size_t)range, sizeof(int));
    int *lev = (int *)malloc((size_t)n * sizeof(int));
    int nlev = 0;

    for (long i = 1; i < n; i++) {
        long a1 = ju[i] - lo, b1 = kv[i] - lo, a2 = ku[i] - lo, b2 = jv[i] - lo;
        int L = 0;
        /* reads: u[ju], v[kv], u[ku] */
        if (uw[a1] > L) L = uw[a1];
        if (vw[b1] > L) L = vw[b1];
        if (uw[a2] > L) L = uw[a2];
        /* writes: u[ju], v[jv] */
        if (ur[a1] > L) L = ur[a1];
        if (vw[b2] > L) L = vw[b2];
        if (vr[b2] > L) L = vr[b2];
        L += 1;
        lev[i] = L;
        if (L > nlev) nlev = L;
        uw[a1] = L;
        vw[b2] = L;
        if (ur[a1] < L) ur[a1] = L;
        if (vr[b1] < L) vr[b1] = L;
        if (ur[a2] < L) ur[a2] = L;
    }
    free(uw); free(ur); free(vw); free(vr);

    /* bucket iterations by level, keeping increasing i inside each level */
    long *start = (long *)calloc((size_t)nlev + 2, sizeof(long));
    long *order = (long *)malloc((size_t)n * sizeof(long));
    for (long i = 1; i < n; i++) start[lev[i] + 1]++;
    for (int L = 1; L <= nlev; L++) start[L + 1] += start[L];
    {
        long *pos = (long *)malloc(((size_t)nlev + 2) * sizeof(long));
        for (int L = 0; L <= nlev + 1; L++) pos[L] = start[L];
        for (long i = 1; i < n; i++) order[pos[lev[i]]++] = i;
        free(pos);
    }
    free(lev);

    /* ---- executor ---- */
    for (int nl = 0; nl < iterations; nl++) {
        for (int L = 1; L <= nlev; L++) {
            long s = start[L], f = start[L + 1];
            #pragma omp parallel for default(none) shared(u, v, c, d, ju, jv, ku, kv, order) firstprivate(s, f) if(f - s > 256) schedule(static)
            for (long t = s; t < f; t++) {
                long i = order[t];
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
