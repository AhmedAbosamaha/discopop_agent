#include "evk/k17.h"
#include <stdlib.h>

static real_t kernel_k17(void)
{
    long k17_n = LEN_1D;

    /* Precompute, per iteration, the wavefront level induced by the
     * cross-iteration RAW on v: iteration i depends on the (unique,
     * since jv is injective) earlier iteration that wrote the slot
     * i reads through kv[i]. Producers are always at a smaller index,
     * so one forward pass is enough. */
    long *k17_depth = (long *)malloc((size_t)k17_n * sizeof(long));
    long *k17_inv_jv = (long *)malloc((size_t)k17_n * sizeof(long));
    for (long k17_p = 0; k17_p < k17_n; k17_p++) {
        k17_inv_jv[k17_p] = -1;
    }

    long k17_max_depth = 0;
    for (long i = 1; i < k17_n; i++) {
        long k17_read_pos = kv[i];
        long k17_producer = (k17_read_pos >= 0 && k17_read_pos < k17_n)
                                 ? k17_inv_jv[k17_read_pos]
                                 : -1;
        k17_depth[i] = (k17_producer >= 0) ? k17_depth[k17_producer] + 1 : 0;
        if (k17_depth[i] > k17_max_depth) {
            k17_max_depth = k17_depth[i];
        }
        long k17_write_pos = jv[i];
        if (k17_write_pos >= 0 && k17_write_pos < k17_n) {
            k17_inv_jv[k17_write_pos] = i;
        }
    }
    free(k17_inv_jv);

    /* Bucket iterations by level (counting sort) so every level can be
     * walked by an independent inner loop. */
    long *k17_count = (long *)calloc((size_t)(k17_max_depth + 2), sizeof(long));
    for (long i = 1; i < k17_n; i++) {
        k17_count[k17_depth[i] + 1]++;
    }
    for (long k17_lvl = 0; k17_lvl <= k17_max_depth; k17_lvl++) {
        k17_count[k17_lvl + 1] += k17_count[k17_lvl];
    }

    long *k17_order = (long *)malloc((size_t)(k17_n - 1) * sizeof(long));
    long *k17_cursor = (long *)malloc((size_t)(k17_max_depth + 1) * sizeof(long));
    for (long k17_lvl = 0; k17_lvl <= k17_max_depth; k17_lvl++) {
        k17_cursor[k17_lvl] = k17_count[k17_lvl];
    }
    for (long i = 1; i < k17_n; i++) {
        long k17_lvl = k17_depth[i];
        k17_order[k17_cursor[k17_lvl]++] = i;
    }
    free(k17_cursor);
    free(k17_depth);

    for (long k17_lvl = 0; k17_lvl <= k17_max_depth; k17_lvl++) {
        long k17_lo = k17_count[k17_lvl];
        long k17_hi = k17_count[k17_lvl + 1];
        for (long k17_k = k17_lo; k17_k < k17_hi; k17_k++) {
            long i = k17_order[k17_k];
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] += u[ku[i]] * d[i];
        }
    }

    free(k17_count);
    free(k17_order);

    return (real_t)0;
}

PB_MAIN(kernel_k17)
