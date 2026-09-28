#include "evk/k42.h"

static real_t kernel_k42(void)
{
    real_t* u_original = (real_t*)malloc(LEN_1D * sizeof(real_t));
    for (long i = 0; i < LEN_1D; i++) {
        u_original[i] = u[i];
    }

    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v[kv[i]] * c[i];
        v[jv[i]] += u_original[ku[i]] * d[i];
    }

    free(u_original);
    return (real_t)0;
}

PB_MAIN(kernel_k42)
