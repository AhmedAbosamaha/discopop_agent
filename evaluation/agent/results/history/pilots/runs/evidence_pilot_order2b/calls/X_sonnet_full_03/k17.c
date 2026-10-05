#include "evk/k17.h"
#include <stdlib.h>

static real_t kernel_k17(void)
{
    long n = LEN_1D;

    /* The only real cross-iteration hazard the profiler saw is a RAW on v:
     * iteration i's read of v[kv[i]] can be fed by an earlier iteration's
     * write to v[jv[i']] (no WAR/WAW was observed on u or v, i.e. each u-
     * and v-location is written by at most one iteration).  We recover,
     * for every iteration, the single earlier iteration (if any) whose
     * write to u or v it actually reads, and assign it a "level" one past
     * that predecessor's level (0 if it has none).  Iterations sharing a
     * level touch no location any other iteration on that level writes or
     * reads, so they may run in any order/in parallel; levels must still
     * be executed in increasing order.  Each iteration still runs its
     * original two statements together and in their original relative
     * order, on values finalized by all earlier levels, so this produces
     * exactly the same sequence of operations - and thus the same result
     * - as the original sweep; only the visitation order of mutually
     * independent iterations changes. */
    if (n > 1) {
        long *last_writer_u = (long *)malloc((size_t)n * sizeof(long));
        long *last_writer_v = (long *)malloc((size_t)n * sizeof(long));
        long *level = (long *)malloc((size_t)n * sizeof(long));

        for (long k = 0; k < n; k++) {
            last_writer_u[k] = -1;
            last_writer_v[k] = -1;
        }

        long max_level = 0;
        for (long i = 1; i < n; i++) {
            long dep = -1;
            long w = last_writer_v[kv[i]];
            if (w > dep) dep = w;
            w = last_writer_u[ku[i]];
            if (w > dep) dep = w;

            level[i] = (dep >= 0) ? level[dep] + 1 : 0;
            if (level[i] > max_level) max_level = level[i];

            last_writer_u[ju[i]] = i;
            last_writer_v[jv[i]] = i;
        }

        long n_levels = max_level + 1;
        long *level_count = (long *)malloc((size_t)n_levels * sizeof(long));
        long *level_start = (long *)malloc((size_t)(n_levels + 1) * sizeof(long));
        long *fill_pos = (long *)malloc((size_t)n_levels * sizeof(long));
        long *order = (long *)malloc((size_t)(n - 1) * sizeof(long));

        for (long L = 0; L < n_levels; L++) level_count[L] = 0;
        for (long i = 1; i < n; i++) level_count[level[i]]++;

        level_start[0] = 0;
        for (long L = 0; L < n_levels; L++) level_start[L + 1] = level_start[L] + level_count[L];
        for (long L = 0; L < n_levels; L++) fill_pos[L] = level_start[L];

        for (long i = 1; i < n; i++) {
            long L = level[i];
            order[fill_pos[L]] = i;
            fill_pos[L]++;
        }

        for (long L = 0; L < n_levels; L++) {
            long lo = level_start[L];
            long hi = level_start[L + 1];
            for (long p = lo; p < hi; p++) {
                long i = order[p];
                u[ju[i]] += v[kv[i]] * c[i];
                v[jv[i]] += u[ku[i]] * d[i];
            }
        }

        free(last_writer_u);
        free(last_writer_v);
        free(level);
        free(level_count);
        free(level_start);
        free(fill_pos);
        free(order);
    }

    return (real_t)0;
}

PB_MAIN(kernel_k17)
