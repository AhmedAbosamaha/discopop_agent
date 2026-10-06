#include <stdlib.h>
#include "data.h"

/* Inspector/executor (level scheduling).
 * The index arrays never change during the kernel, so the dependence
 * structure of the i-loop is computed once: every iteration gets a level
 * strictly greater than the level of every earlier iteration it conflicts
 * with (RAW, WAR, WAW on u, v, w).  Iterations of one level touch disjoint
 * written locations, so each level runs as an independent parallel loop,
 * and all conflicting accesses keep their original relative order. */

static inline int imax(int x, int y) { return x > y ? x : y; }

real_t kernel_k27(void)
{
    const long n = LEN_1D;
    long M = 0;

#pragma omp parallel for reduction(max:M)
    for (long i = 1; i < n; i++) {
        long m = ju[i];
        if (jv[i] > m) m = jv[i];
        if (jw[i] > m) m = jw[i];
        if (ku[i] > m) m = ku[i];
        if (kv[i] > m) m = kv[i];
        if (kw[i] > m) m = kw[i];
        if (m > M) M = m;
    }
    M += 1;

    int *uW = (int *)malloc(sizeof(int) * M);
    int *uR = (int *)malloc(sizeof(int) * M);
    int *vW = (int *)malloc(sizeof(int) * M);
    int *vR = (int *)malloc(sizeof(int) * M);
    int *wW = (int *)malloc(sizeof(int) * M);
    int *wR = (int *)malloc(sizeof(int) * M);
    int *lev = (int *)malloc(sizeof(int) * (n > 0 ? n : 1));

#pragma omp parallel for
    for (long k = 0; k < M; k++) {
        uW[k] = -1; uR[k] = -1;
        vW[k] = -1; vR[k] = -1;
        wW[k] = -1; wR[k] = -1;
    }

    /* inspector: sequential, O(n) */
    int nlev = 0;
    for (long i = 1; i < n; i++) {
        int a1 = ju[i], b1 = kw[i], c1 = ku[i], d1 = jv[i], e1 = kv[i], f1 = jw[i];
        int L = 0;
        /* reads */
        L = imax(L, wW[b1] + 1);
        L = imax(L, uW[c1] + 1);
        L = imax(L, vW[e1] + 1);
        /* writes (u[ju] is also read) */
        L = imax(L, uW[a1] + 1); L = imax(L, uR[a1] + 1);
        L = imax(L, vW[d1] + 1); L = imax(L, vR[d1] + 1);
        L = imax(L, wW[f1] + 1); L = imax(L, wR[f1] + 1);
        lev[i] = L;
        wR[b1] = imax(wR[b1], L);
        uR[c1] = imax(uR[c1], L);
        vR[e1] = imax(vR[e1], L);
        uR[a1] = imax(uR[a1], L);
        uW[a1] = L;
        vW[d1] = L;
        wW[f1] = L;
        if (L + 1 > nlev) nlev = L + 1;
    }
    free(uW); free(uR); free(vW); free(vR); free(wW); free(wR);

    /* counting sort of iterations by level (stable in i) */
    long *start = (long *)calloc((size_t)nlev + 1, sizeof(long));
    int *order = (int *)malloc(sizeof(int) * (n > 0 ? n : 1));
    for (long i = 1; i < n; i++) start[lev[i] + 1]++;
    for (int l = 0; l < nlev; l++) start[l + 1] += start[l];
    {
        long *pos = (long *)malloc(sizeof(long) * ((size_t)nlev + 1));
        for (int l = 0; l <= nlev; l++) pos[l] = start[l];
        for (long i = 1; i < n; i++) order[pos[lev[i]]++] = (int)i;
        free(pos);
    }
    free(lev);

    /* executor */
    for (int nl = 0; nl < iterations; nl++) {
        for (int l = 0; l < nlev; l++) {
            const long lo = start[l], hi = start[l + 1];
#pragma omp parallel for shared(order) schedule(static)
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
