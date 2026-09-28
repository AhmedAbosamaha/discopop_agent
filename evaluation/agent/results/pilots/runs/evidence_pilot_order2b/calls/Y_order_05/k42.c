#include "evk/k42.h"

static real_t kernel_k42(void)
{
    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v[kv[i]] * c[i];
    }
    for (long i = 1; i < LEN_1D; i++) {
        v[jv[i]] += u[ku[i]] * d[i];
    }
    return (real_t)0;
}

PB_MAIN(kernel_k42)
