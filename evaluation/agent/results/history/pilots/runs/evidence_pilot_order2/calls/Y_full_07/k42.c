#include "evk/k42.h"

static real_t kernel_k42(void)
{
    real_t *u_buffer = (real_t *)malloc(LEN_1D * sizeof(real_t));
    memcpy(u_buffer, u, LEN_1D * sizeof(real_t));

    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v[kv[i]] * c[i];
        v[jv[i]] += u_buffer[ku[i]] * d[i];
    }

    free(u_buffer);
    return (real_t)0;
}

PB_MAIN(kernel_k42)
