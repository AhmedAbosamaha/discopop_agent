#include "evk/k42.h"

static real_t kernel_k42(void)
{
    real_t *temp_u = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *temp_v = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (long i = 0; i < LEN_1D; i++) {
        temp_u[i] = 0;
        temp_v[i] = 0;
    }

    for (long i = 1; i < LEN_1D; i++) {
        temp_u[ju[i]] += v[kv[i]] * c[i];
        temp_v[jv[i]] += u[ku[i]] * d[i];
    }

    for (long i = 0; i < LEN_1D; i++) {
        u[i] += temp_u[i];
        v[i] += temp_v[i];
    }

    free(temp_u);
    free(temp_v);

    return (real_t)0;
}

PB_MAIN(kernel_k42)
