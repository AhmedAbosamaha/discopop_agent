#include "evk/k17.h"

static real_t kernel_k17(void)
{
    for (long col = 0; col < 2; col++) {
        for (long i = 1 + col; i < LEN_1D; i += 2) {
            u[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] += u[ku[i]] * d[i];
        }
    }
    return (real_t)0;
}

PB_MAIN(kernel_k17)
