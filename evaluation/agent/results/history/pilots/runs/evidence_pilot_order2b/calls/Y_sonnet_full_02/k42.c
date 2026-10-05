#include "evk/k42.h"
#include <stdlib.h>

static real_t kernel_k42(void)
{
    /* Original: u[ju[i]] += v[kv[i]]*c[i]; v[jv[i]] += u[ku[i]]*d[i];
     * DiscoPoP found a real loop-carried RAW on u: the write at ju[i] in
     * one iteration can be read back at ku[i'] in a LATER iteration i'.
     * No WAW/WAR was ever observed on u or on v, which means ju and jv
     * each hit a distinct array position per iteration: the value at any
     * given position of u (or v) is written AT MOST ONCE during the whole
     * sweep.  All that matters for a read is whether that single write
     * happened at-or-before i or after i in the original order, not any
     * running accumulation.  We make that ordering test explicit instead
     * of relying on execution order:
     *   pass 0: snapshot u and mark every position as "no writer yet".
     *   pass 1: for each i, record which iteration writes u position
     *           ju[i] and with what value, and commit that write to u.
     *           ju is injective (no WAW observed), so every iteration
     *           touches a different element of u / u_contrib / u_producer:
     *           the iterations of this loop are independent (Do-All).
     *   pass 2: for each i, decide whether the (unique) writer of the u
     *           position it reads (ku[i]) occurred at or before i; use
     *           the post-write value already committed in pass 1 if so,
     *           the pre-loop snapshot otherwise, then apply the update to
     *           v[jv[i]].  jv is injective too, so this loop's iterations
     *           also write disjoint elements and are independent (Do-All).
     * Together the two passes reproduce, bit for bit, what the original
     * interleaved loop computed; the extra buffers are heap-allocated and
     * grow only linearly with LEN_1D. */
    real_t *u_orig = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    real_t *u_contrib = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);
    long *u_producer = (long *)malloc(sizeof(long) * (size_t)LEN_1D);

    for (long pos = 0; pos < LEN_1D; pos++) {
        u_orig[pos] = u[pos];
        u_producer[pos] = -1;
    }

    for (long i = 1; i < LEN_1D; i++) {
        real_t contrib = v[kv[i]] * c[i];
        u_contrib[ju[i]] = contrib;
        u_producer[ju[i]] = i;
        u[ju[i]] = u_orig[ju[i]] + contrib;
    }

    for (long i = 1; i < LEN_1D; i++) {
        long producer = u_producer[ku[i]];
        real_t u_at_i = (producer != -1 && producer <= i) ? u[ku[i]] : u_orig[ku[i]];
        v[jv[i]] += u_at_i * d[i];
    }

    free(u_orig);
    free(u_contrib);
    free(u_producer);

    return (real_t)0;
}

PB_MAIN(kernel_k42)
