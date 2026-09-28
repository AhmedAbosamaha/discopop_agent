#include "evk/k17.h"

static real_t kernel_k17(void)
{
    for (long i = 1; i < LEN_1D; i++) {
        /* Stage 1: produce a new u element from the current v element.
         * u's own indices never alias across iterations (DiscoPoP found no
         * loop-carried dependence on u), so this stage's memory effects are
         * fully local to iteration i once the v value it needs is in hand. */
        const real_t v_in = v[kv[i]];
        u[ju[i]] += v_in * c[i];

        /* Stage 2: produce a new v element from the u element stage 1 just
         * made available. This is the sole loop-carried RAW (through v):
         * some later iteration's v_in above reads exactly the value this
         * stage stores here. Keeping the store as the last, isolated action
         * of the iteration preserves the original inter-iteration order of
         * v accesses exactly (same values, same sequence), while making the
         * producer/consumer relationship between the two stages explicit. */
        const real_t u_out = u[ku[i]];
        v[jv[i]] += u_out * d[i];
    }
    return (real_t)0;
}

PB_MAIN(kernel_k17)
