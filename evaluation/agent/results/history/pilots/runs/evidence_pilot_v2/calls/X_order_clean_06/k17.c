#include "evk/k17.h"

static real_t kernel_k17(void)
{
    // Pass 1: update v with u values (no dependence on v in this loop)
    for (long i = 1; i < LEN_1D; i++) {
        v[jv[i]] += u[ku[i]] * d[i];
    }

    // Pass 2: update u with v values (v is fully computed, can be parallelized)
    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v[kv[i]] * c[i];
    }

    return (real_t)0;
}

PB_MAIN(kernel_k17)
