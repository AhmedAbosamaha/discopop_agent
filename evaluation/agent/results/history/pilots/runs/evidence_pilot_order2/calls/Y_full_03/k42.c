#include "evk/k42.h"

static real_t kernel_k42(void)
{
    real_t *u_new = (real_t*)malloc(sizeof(real_t) * LEN_1D);
    for (long i = 0; i < LEN_1D; i++) {
        u_new[i] = u[i];
    }

    for (long i = 1; i < LEN_1D; i++) {
        u_new[ju[i]] += v[kv[i]] * c[i];
        v[jv[i]] += u[ku[i]] * d[i];
    }

    for (long i = 0; i < LEN_1D; i++) {
        u[i] = u_new[i];
    }
    free(u_new);

    return (real_t)0;
}

PB_MAIN(kernel_k42)
