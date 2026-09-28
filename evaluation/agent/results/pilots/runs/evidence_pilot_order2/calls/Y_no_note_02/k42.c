#include "evk/k42.h"

static real_t kernel_k42(void)
{
    real_t *u_read = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (long i = 1; i < LEN_1D; i++) {
        u_read[i] = u[ku[i]];
    }

    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v[kv[i]] * c[i];
        v[jv[i]] += u_read[i] * d[i];
    }

    free(u_read);
    return (real_t)0;
}

PB_MAIN(kernel_k42)
