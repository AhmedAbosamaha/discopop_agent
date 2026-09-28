#include "evk/k17.h"

static void k17_step(long i)
{
    u[ju[i]] += v[kv[i]] * c[i];
    v[jv[i]] += u[ku[i]] * d[i];
}

static real_t kernel_k17(void)
{
    for (long i = 1; i < LEN_1D; i++) {
        k17_step(i);
    }
    return (real_t)0;
}

PB_MAIN(kernel_k17)
