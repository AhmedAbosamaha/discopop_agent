#include "data.h"
#include <stdlib.h>

real_t kernel_k19(void)
{
    const long n = LEN_1D;

    if (n <= 1) {
        for (int nl = 0; nl < iterations; nl++) {
            dummy(a, b, c, d, e);
        }
        return (real_t)0;
    }

    /* ---- Inspector: build a level schedule from the index arrays ----
     * Iteration i touches: u[ju[i]] (read+write), u[ku[i]] (read),
     *                      v[kv[i]] (read),        v[jv[i]] (write).
     * level[i] = 1 + max(dependence levels), where a read depends on the
     * last write of its location and a write depends on the last write and
     * the last read of its location.  Conflicting iterations therefore land
     * in strictly increasing levels in program order; within a level every
     * location is read-only. */
    long maxU = 0, maxV = 0;
    for (long i = 1; i < n; i++) {
        if (ju[i] > maxU) maxU = ju[i];
        if (ku[i] > maxU) maxU = ku[i];
        if (jv[i] > maxV) maxV = jv[i];
        if (kv[i] > maxV) maxV = kv[i];
    }

    int *lastWU = (int *)calloc((size_t)(maxU + 1), sizeof(int));
    int *lastRU = (int *)calloc((size_t)(maxU + 1), sizeof(int));
    int *lastWV = (int *)calloc((size_t)(maxV + 1), sizeof(int));
    int *lastRV = (int *)calloc((size_t)(maxV + 1), sizeof(int));
    int *level  = (int *)malloc((size_t)n * sizeof(int));
    long *order = (long *)malloc((size_t)n * sizeof(long));

    int nlev = 0;
    for (long i = 1; i < n; i++) {
        int a_u = ju[i];
        int r_u = ku[i];
        int r_v = kv[i];
        int w_v = jv[i];
        int dep = 0;
        /* read-modify-write of u[a_u] */
        if (lastWU[a_u] > dep) dep = lastWU[a_u];
        if (lastRU[a_u] > dep) dep = lastRU[a_u];
        /* read of u[r_u] */
        if (lastWU[r_u] > dep) dep = lastWU[r_u];
        /* read of v[r_v] */
        if (lastWV[r_v] > dep) dep = lastWV[r_v];
        /* write of v[w_v] */
        if (lastWV[w_v] > dep) dep = lastWV[w_v];
        if (lastRV[w_v] > dep) dep = lastRV[w_v];
        int lv = dep + 1;
        level[i] = lv;
        if (lv > nlev) nlev = lv;
        lastWU[a_u] = lv; lastRU[a_u] = lv;
        if (lv > lastRU[r_u]) lastRU[r_u] = lv;
        if (lv > lastRV[r_v]) lastRV[r_v] = lv;
        lastWV[w_v] = lv;
        if (lv > lastRV[w_v]) lastRV[w_v] = lv;
    }

    free(lastWU);
    free(lastRU);
    free(lastWV);
    free(lastRV);

    /* counting sort of iterations by level: off[lv] .. off[lv+1] */
    long *off = (long *)calloc((size_t)(nlev + 2), sizeof(long));
    for (long i = 1; i < n; i++) {
        off[level[i] + 1]++;
    }
    for (int lv = 1; lv <= nlev; lv++) {
        off[lv + 1] += off[lv];
    }
    {
        long *pos = (long *)malloc((size_t)(nlev + 2) * sizeof(long));
        for (int lv = 0; lv <= nlev + 1; lv++) pos[lv] = off[lv];
        for (long i = 1; i < n; i++) {
            order[pos[level[i]]++] = i;
        }
        free(pos);
    }
    free(level);

    /* ---- Executor ---- */
    for (int nl = 0; nl < iterations; nl++) {
        for (int lv = 1; lv <= nlev; lv++) {
            long start = off[lv];
            long end = off[lv + 1];
            #pragma omp parallel for shared(order, u, v, c, d, ju, jv, ku, kv) \
                firstprivate(start, end) if(end - start >= 128)
            for (long k = start; k < end; k++) {
                long i = order[k];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(off);
    free(order);
    return (real_t)0;
}
