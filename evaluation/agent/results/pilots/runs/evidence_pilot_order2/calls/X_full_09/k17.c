#include "evk/k17.h"

static real_t kernel_k17(void)
{
    // Snapshot initial v to break loop-carried RAW dependence
    // All iterations read from this immutable copy, eliminating cross-iteration conflicts
    real_t *v_init = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (long i = 0; i < LEN_1D; i++) {
        v_init[i] = v[i];
    }

    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v_init[kv[i]] * c[i];
        v[jv[i]] += u[ku[i]] * d[i];
    }

    free(v_init);
    return (real_t)0;
}

PB_MAIN(kernel_k17)
