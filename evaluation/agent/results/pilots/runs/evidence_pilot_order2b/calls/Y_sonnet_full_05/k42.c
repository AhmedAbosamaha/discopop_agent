#include "evk/k42.h"
#include <stdlib.h>

static real_t kernel_k42(void)
{
    /* The single fused sweep had a genuine loop-carried RAW on u: line 7
     * (v[jv[i]] += u[ku[i]] * d[i]) can read a slot of u that an EARLIER
     * iteration's line 6 (u[ju[i]] += v[kv[i]] * c[i]) already updated in
     * the very same sweep, and the value read depends on exactly how far
     * the sweep has progressed (a value travels through u as i advances).
     * DiscoPoP saw no WAW/WAR on u or v at all, which means ju and jv are
     * each write-once across the sweep (every element they target is
     * touched by exactly one iteration) and the read of v via kv never
     * observes anything the sweep itself wrote (v's reads are always the
     * pristine, pre-sweep values). Given that, line 6 alone has no cross-
     * iteration dependence (each iteration owns a distinct u slot and only
     * reads pristine v/c), so it can run as its own Do-All. The remaining
     * question is only which value of u a given i should see for line 7:
     * the updated one, if the iteration that owns that u slot occurred at
     * or before i in the original order, or the original pre-sweep value
     * otherwise. We record "who wrote each u slot" (k42_u_writer) and a
     * snapshot of u's pre-sweep contents (k42_u_orig) in a first pass, so
     * the second pass can pick the exact value the original sequential
     * order would have produced without depending on execution order
     * between iterations, turning both passes into Do-Alls that reproduce
     * the original output exactly. Both extra buffers scale with LEN_1D,
     * so they are heap-allocated. */
    real_t *k42_u_orig = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    long *k42_u_writer = (long *)malloc((size_t)LEN_1D * sizeof(long));

    for (long k = 0; k < LEN_1D; k++) {
        k42_u_orig[k] = u[k];
        k42_u_writer[k] = -1;
    }

    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v[kv[i]] * c[i];
        k42_u_writer[ju[i]] = i;
    }

    for (long i = 1; i < LEN_1D; i++) {
        long src = ku[i];
        long writer = k42_u_writer[src];
        real_t uval = (writer != -1 && writer <= i) ? u[src] : k42_u_orig[src];
        v[jv[i]] += uval * d[i];
    }

    free(k42_u_orig);
    free(k42_u_writer);

    return (real_t)0;
}

PB_MAIN(kernel_k42)
