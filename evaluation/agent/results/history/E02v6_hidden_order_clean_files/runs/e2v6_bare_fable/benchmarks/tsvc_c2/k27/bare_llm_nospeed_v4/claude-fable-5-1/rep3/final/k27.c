#include <stdlib.h>
#include "data.h"

real_t kernel_k27(void)
{
    const long n = LEN_1D;

    /* ------------------------------------------------------------------
     * Inspector: the index arrays never change, so the dependence graph of
     * the i-loop is the same for every nl.  Assign each iteration i a
     * wavefront level such that every iteration it depends on (through
     * u, v or w, flow / anti / output) sits in a strictly lower level.
     * Iterations within one level are mutually independent.
     * ------------------------------------------------------------------ */
    long maxidx = 0;
    #pragma omp parallel for reduction(max:maxidx) shared(ju, jv, jw, ku, kv, kw) schedule(static)
    for (long i = 1; i < n; i++) {
        long m = ju[i];
        if (jv[i] > m) m = jv[i];
        if (jw[i] > m) m = jw[i];
        if (ku[i] > m) m = ku[i];
        if (kv[i] > m) m = kv[i];
        if (kw[i] > m) m = kw[i];
        if (m > maxidx) maxidx = m;
    }
    const long span = maxidx + 1;          /* keys: u -> [0,span), v -> [span,2span), w -> [2span,3span) */
    const long nkeys = 3 * span;

    int *lastW = (int *)malloc((size_t)nkeys * sizeof(int));
    int *lastR = (int *)malloc((size_t)nkeys * sizeof(int));
    int *level = (int *)malloc((size_t)n * sizeof(int));

    #pragma omp parallel for shared(lastW, lastR) firstprivate(nkeys) schedule(static)
    for (long k = 0; k < nkeys; k++) {
        lastW[k] = -1;
        lastR[k] = -1;
    }

    int maxlvl = -1;
    for (long i = 1; i < n; i++) {
        const long r_u1 = ju[i];               /* u[ju[i]] read (+=) and written */
        const long r_w  = 2 * span + kw[i];    /* w[kw[i]] read */
        const long r_u2 = ku[i];               /* u[ku[i]] read */
        const long r_v  = span + kv[i];        /* v[kv[i]] read */
        const long w_u  = ju[i];               /* u[ju[i]] written */
        const long w_v  = span + jv[i];        /* v[jv[i]] written */
        const long w_w  = 2 * span + jw[i];    /* w[jw[i]] written */

        int lvl = 0;
        /* reads must follow the last write of that location */
        if (lastW[r_u1] + 1 > lvl) lvl = lastW[r_u1] + 1;
        if (lastW[r_w]  + 1 > lvl) lvl = lastW[r_w]  + 1;
        if (lastW[r_u2] + 1 > lvl) lvl = lastW[r_u2] + 1;
        if (lastW[r_v]  + 1 > lvl) lvl = lastW[r_v]  + 1;
        /* writes must follow the last write and the last read of that location */
        if (lastW[w_u] + 1 > lvl) lvl = lastW[w_u] + 1;
        if (lastR[w_u] + 1 > lvl) lvl = lastR[w_u] + 1;
        if (lastW[w_v] + 1 > lvl) lvl = lastW[w_v] + 1;
        if (lastR[w_v] + 1 > lvl) lvl = lastR[w_v] + 1;
        if (lastW[w_w] + 1 > lvl) lvl = lastW[w_w] + 1;
        if (lastR[w_w] + 1 > lvl) lvl = lastR[w_w] + 1;

        level[i] = lvl;
        if (lvl > maxlvl) maxlvl = lvl;

        if (lvl > lastR[r_u1]) lastR[r_u1] = lvl;
        if (lvl > lastR[r_w])  lastR[r_w]  = lvl;
        if (lvl > lastR[r_u2]) lastR[r_u2] = lvl;
        if (lvl > lastR[r_v])  lastR[r_v]  = lvl;
        lastW[w_u] = lvl;
        lastW[w_v] = lvl;
        lastW[w_w] = lvl;
    }
    free(lastW);
    free(lastR);

    /* counting sort of the iterations 1..n-1 by level */
    const long nlev = (long)maxlvl + 1;
    long *off  = (long *)calloc((size_t)nlev + 1, sizeof(long));
    long *fill = (long *)malloc(((size_t)nlev + 1) * sizeof(long));
    int  *order = (int *)malloc((size_t)n * sizeof(int));

    for (long i = 1; i < n; i++) off[level[i] + 1]++;
    for (long L = 0; L < nlev; L++) off[L + 1] += off[L];
    for (long L = 0; L <= nlev; L++) fill[L] = off[L];
    for (long i = 1; i < n; i++) order[fill[level[i]]++] = (int)i;
    free(fill);
    free(level);

    /* ------------------------------------------------------------------
     * Executor: levels run in order (this serial loop carries the moved
     * dependence); the iterations inside one level are independent.
     * ------------------------------------------------------------------ */
    for (int nl = 0; nl < iterations; nl++) {
        for (long L = 0; L < nlev; L++) {
            const long lo = off[L];
            const long hi = off[L + 1];
            #pragma omp parallel for shared(order, u, v, w, c, d, e, ju, jv, jw, ku, kv, kw) firstprivate(lo, hi) schedule(static) if (hi - lo >= 64)
            for (long p = lo; p < hi; p++) {
                const long i = order[p];
                u[ju[i]] += w[kw[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
                w[jw[i]] = v[kv[i]] * e[i] + d[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(order);
    free(off);
    return (real_t)0;
}
