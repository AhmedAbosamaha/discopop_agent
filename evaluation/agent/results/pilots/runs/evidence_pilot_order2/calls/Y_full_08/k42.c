#include "evk/k42.h"

static real_t kernel_k42(void)
{
    // Phase 1: Update all u values
    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v[kv[i]] * c[i];
    }
    // Phase 2: Update all v values using the updated u
    for (long i = 1; i < LEN_1D; i++) {
        v[jv[i]] += u[ku[i]] * d[i];
    }
    return (real_t)0;
}

PB_MAIN(kernel_k42)
