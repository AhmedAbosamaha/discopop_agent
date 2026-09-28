#include "evk/k17.h"
#include <stdlib.h>

static real_t kernel_k17(void)
{
    long n = LEN_1D;

    /* The observed blocker is a genuine RAW on v: an earlier iteration's
     * write v[jv[i]] can be read by a later iteration's v[kv[i2]] (and the
     * same shape applies to u through ju/ku). Because ju/ku/jv/kv are
     * arbitrary index arrays, the distance a value travels is not fixed,
     * so neither a plain double buffer (it would make later iterations
     * see stale, pre-sweep values -- verified wrong per the evidence)
     * nor a small fixed-offset block split is safe in general.
     *
     * What is safe and general: compute, once, a dependency "level" for
     * every iteration -- 0 if the u/v locations it reads were never
     * produced earlier in this loop, otherwise one more than the level of
     * whichever earlier iteration last produced that location -- then run
     * the loop in level order. All iterations sharing a level are
     * mutually independent by construction (any producer of a value a
     * level-L iteration reads sits strictly below level L), so the inner
     * pass over one level is a genuine Do-All; only the (small) number of
     * levels is executed in sequence, so the exact original value flow is
     * preserved. This is O(n) bookkeeping (one forward pass plus a
     * counting sort by level), not O(n^2), and every auxiliary buffer is
     * heap-allocated since its size scales with LEN_1D.
     */
    long *level = (long *)malloc((size_t)n * sizeof(long));
    long *last_writer_u = (long *)malloc((size_t)n * sizeof(long));
    long *last_writer_v = (long *)malloc((size_t)n * sizeof(long));
    long *level_count = (long *)malloc((size_t)n * sizeof(long));
    long *level_start = (long *)malloc((size_t)(n + 1) * sizeof(long));
    long *fill_pos = (long *)malloc((size_t)n * sizeof(long));
    long *iter_order = (long *)malloc((size_t)n * sizeof(long));

    for (long k = 0; k < n; k++) {
        last_writer_u[k] = -1;
        last_writer_v[k] = -1;
        level_count[k] = 0;
        level[k] = 0;
    }

    long max_level = 0;
    for (long i = 1; i < n; i++) {
        long loc_v = kv[i];
        long loc_u = ku[i];
        long pv = last_writer_v[loc_v];
        long pu = last_writer_u[loc_u];
        long lvl = 0;
        if (pv >= 0) {
            long cand = level[pv] + 1;
            if (cand > lvl) lvl = cand;
        }
        if (pu >= 0) {
            long cand = level[pu] + 1;
            if (cand > lvl) lvl = cand;
        }
        level[i] = lvl;
        if (lvl > max_level) max_level = lvl;
        level_count[lvl]++;

        last_writer_u[ju[i]] = i;
        last_writer_v[jv[i]] = i;
    }

    level_start[0] = 0;
    for (long L = 0; L <= max_level; L++) {
        level_start[L + 1] = level_start[L] + level_count[L];
        fill_pos[L] = level_start[L];
    }
    for (long i = 1; i < n; i++) {
        long L = level[i];
        iter_order[fill_pos[L]] = i;
        fill_pos[L]++;
    }

    for (long L = 0; L <= max_level; L++) {
        long s = level_start[L];
        long e = level_start[L + 1];
        for (long p = s; p < e; p++) {
            long i = iter_order[p];
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] += u[ku[i]] * d[i];
        }
    }

    free(level);
    free(last_writer_u);
    free(last_writer_v);
    free(level_count);
    free(level_start);
    free(fill_pos);
    free(iter_order);

    return (real_t)0;
}

PB_MAIN(kernel_k17)
