#include "evk/k17.h"

static real_t kernel_k17(void)
{
    for (long i = 1; i < LEN_1D; i++) {
        v[jv[i]] += u[ku[i]] * d[i];
    }
    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v[kv[i]] * c[i];
    }
    return (real_t)0;
}

PB_MAIN(kernel_k17)
