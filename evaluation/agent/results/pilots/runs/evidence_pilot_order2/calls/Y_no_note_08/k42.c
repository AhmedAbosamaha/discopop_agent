#include "evk/k42.h"

static real_t kernel_k42(void)
{
    real_t *u_accum = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    for (long i = 0; i < LEN_1D; i++) {
        u_accum[i] = u[i];
    }

    for (long i = 1; i < LEN_1D; i++) {
        u_accum[ju[i]] += v[kv[i]] * c[i];
    }
    for (long i = 1; i < LEN_1D; i++) {
        v[jv[i]] += u_accum[ku[i]] * d[i];
    }

    for (long i = 0; i < LEN_1D; i++) {
        u[i] = u_accum[i];
    }
    free(u_accum);
    return (real_t)0;
}

PB_MAIN(kernel_k42)
