#include "data.h"
#include <stdlib.h>

/*
 * Inspector/executor parallelization.
 *
 * The inner loop carries true dependences through the indirectly addressed
 * arrays u and v (iteration i updates u[ju[i]] and v[jv[i]]; later iterations
 * may read or write the same slots through ku/kv/ju/jv).  The index arrays
 * never change across the nl loop (dummy only touches a..e), so they are
 * inspected once: every iteration i gets a level equal to 1 + the highest
 * level of any earlier iteration that conflicts with it (write/write,
 * write/read or read/write on the same u or v slot).  Iterations sharing a
 * level therefore touch pairwise disjoint u/v slots (or only read a common
 * slot), so each level can run in parallel in any order and every read sees
 * exactly the value the serial program would have produced.  Levels are
 * executed in increasing order; the barrier at the end of each parallel loop
 * carries the dependence from one level to the next.
 */
real_t kernel_k48(void)
{
    const long n = LEN_1D;

    /* ---------- inspector (runs once, O(n)) ---------- */
    long maxidx = 0;
#pragma omp parallel for shared(ju, jv, ku, kv) reduction(max : maxidx)
    for (long i = 1; i < n; i++) {
        if ((long)ju[i] > maxidx) maxidx = ju[i];
        if ((long)jv[i] > maxidx) maxidx = jv[i];
        if ((long)ku[i] > maxidx) maxidx = ku[i];
        if ((long)kv[i] > maxidx) maxidx = kv[i];
    }

    int *lastWU = (int *)calloc((size_t)maxidx + 1, sizeof(int));
    int *lastRU = (int *)calloc((size_t)maxidx + 1, sizeof(int));
    int *lastWV = (int *)calloc((size_t)maxidx + 1, sizeof(int));
    int *lastRV = (int *)calloc((size_t)maxidx + 1, sizeof(int));
    int *level  = (int *)malloc((size_t)(n > 0 ? n : 1) * sizeof(int));

    if (!lastWU || !lastRU || !lastWV || !lastRV || !level) {
        /* allocation failure: fall back to the original serial code */
        free(lastWU); free(lastRU); free(lastWV); free(lastRV); free(level);
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
    for (long i = 1; i < n; i++) {
        const int wu = ju[i];   /* u slot read-modify-written */
        const int ru = ku[i];   /* u slot read */
        const int wv = jv[i];   /* v slot written */
        const int rv = kv[i];   /* v slot read */
        int L = lastWU[wu];
        if (lastRU[wu] > L) L = lastRU[wu];
        if (lastWU[ru] > L) L = lastWU[ru];
        if (lastWV[wv] > L) L = lastWV[wv];
        if (lastRV[wv] > L) L = lastRV[wv];
        if (lastWV[rv] > L) L = lastWV[rv];
        L += 1;
        level[i] = L;
        if (L > nlev) nlev = L;
        lastWU[wu] = L;
        lastRU[wu] = L;
        if (lastRU[ru] < L) lastRU[ru] = L;
        lastWV[wv] = L;
        if (lastRV[rv] < L) lastRV[rv] = L;
    }
    free(lastWU); free(lastRU); free(lastWV); free(lastRV);

    /* counting sort of iterations by level: level L owns order[start[L] .. start[L+1]) */
    int *start = (int *)calloc((size_t)nlev + 2, sizeof(int));
    int *fill  = (int *)malloc(((size_t)nlev + 2) * sizeof(int));
    int *order = (int *)malloc((size_t)(n > 0 ? n : 1) * sizeof(int));

    if (!start || !fill || !order) {
        free(start); free(fill); free(order); free(level);
        for (int nl = 0; nl < iterations; nl++) {
            for (long i = 1; i < LEN_1D; i++) {
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] = u[ku[i]] * d[i] + c[i];
            }
            dummy(a, b, c, d, e);
        }
        return (real_t)0;
    }

    for (long i = 1; i < n; i++) start[level[i] + 1]++;
    for (int L = 1; L <= nlev; L++) start[L + 1] += start[L];
    for (int L = 0; L <= nlev + 1; L++) fill[L] = start[L];
    for (long i = 1; i < n; i++) order[fill[level[i]]++] = (int)i;
    free(fill);
    free(level);

    /* ---------- executor ---------- */
    for (int nl = 0; nl < iterations; nl++) {
        for (int L = 1; L <= nlev; L++) {
            int lo = start[L];
            int hi = start[L + 1];
            /* iterations in one level touch pairwise disjoint u/v slots */
#pragma omp parallel for shared(order, u, v, c, d, ju, jv, ku, kv) \
        firstprivate(lo, hi) if (hi - lo > 16)
            for (int p = lo; p < hi; p++) {
                const int i = order[p];
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
