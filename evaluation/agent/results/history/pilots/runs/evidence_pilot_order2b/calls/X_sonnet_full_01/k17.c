#include "evk/k17.h"
#include <stdlib.h>

static real_t kernel_k17(void)
{
    long N = LEN_1D;

    /* Each u/v location is written by at most one iteration (no WAW was
       observed), so for every iteration i there is at most one earlier
       iteration whose write it actually consumes through ju/ku/jv/kv.
       Find that unique producer (if any) in one sequential pass and
       derive a dependency "level" from it: level 0 = depends only on
       data that existed before the loop started; level L+1 = depends on
       a level-L iteration. Iterations that land on the same level never
       depend on each other (a same-level dependency would force a level
       difference), so a level can be swept in any order; levels
       themselves must still be swept in increasing order, since that is
       the order the real data actually becomes available in. */
    long *k17_inv_ju = (long *)malloc((size_t)N * sizeof(long));
    long *k17_inv_jv = (long *)malloc((size_t)N * sizeof(long));
    long *k17_level = (long *)malloc((size_t)N * sizeof(long));
    for (long k = 0; k < N; k++) {
        k17_inv_ju[k] = -1;
        k17_inv_jv[k] = -1;
        k17_level[k] = 0;
    }

    long k17_max_level = 0;
    for (long i = 1; i < N; i++) {
        long wU = k17_inv_ju[ku[i]];
        long wV = k17_inv_jv[kv[i]];
        long lvl = 0;
        if (wU != -1 && k17_level[wU] + 1 > lvl) lvl = k17_level[wU] + 1;
        if (wV != -1 && k17_level[wV] + 1 > lvl) lvl = k17_level[wV] + 1;
        k17_level[i] = lvl;
        if (lvl > k17_max_level) k17_max_level = lvl;
        k17_inv_ju[ju[i]] = i;
        k17_inv_jv[jv[i]] = i;
    }

    /* Counting sort of iterations 1..N-1 by level, so each level's
       members occupy a contiguous range of k17_order. */
    long *k17_count = (long *)malloc((size_t)(k17_max_level + 2) * sizeof(long));
    long *k17_offset = (long *)malloc((size_t)(k17_max_level + 2) * sizeof(long));
    long *k17_fill = (long *)malloc((size_t)(k17_max_level + 1) * sizeof(long));
    long *k17_order = (long *)malloc((size_t)N * sizeof(long));
    for (long k = 0; k <= k17_max_level; k++) k17_count[k] = 0;
    for (long i = 1; i < N; i++) k17_count[k17_level[i]]++;
    k17_offset[0] = 0;
    for (long k = 0; k <= k17_max_level; k++) k17_offset[k + 1] = k17_offset[k] + k17_count[k];
    for (long k = 0; k <= k17_max_level; k++) k17_fill[k] = k17_offset[k];
    for (long i = 1; i < N; i++) {
        k17_order[k17_fill[k17_level[i]]] = i;
        k17_fill[k17_level[i]]++;
    }

    for (long lvl = 0; lvl <= k17_max_level; lvl++) {
        long lo = k17_offset[lvl];
        long hi = k17_offset[lvl + 1];
        for (long p = lo; p < hi; p++) {
            long i = k17_order[p];
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] += u[ku[i]] * d[i];
        }
    }

    free(k17_inv_ju);
    free(k17_inv_jv);
    free(k17_level);
    free(k17_count);
    free(k17_offset);
    free(k17_fill);
    free(k17_order);

    return (real_t)0;
}

PB_MAIN(kernel_k17)
