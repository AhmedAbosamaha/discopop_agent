#include "evk/k42.h"

static real_t kernel_k42(void)
{
    real_t *u_temp = malloc(sizeof(real_t) * LEN_1D);
    real_t *v_temp = malloc(sizeof(real_t) * LEN_1D);

    for (long i = 0; i < LEN_1D; i++) {
        u_temp[i] = u[i];
        v_temp[i] = v[i];
    }

    for (long i = 1; i < LEN_1D; i++) {
        u_temp[ju[i]] += v_temp[kv[i]] * c[i];
    }

    for (long i = 1; i < LEN_1D; i++) {
        v_temp[jv[i]] += u_temp[ku[i]] * d[i];
    }

    for (long i = 0; i < LEN_1D; i++) {
        u[i] = u_temp[i];
        v[i] = v_temp[i];
    }

    free(u_temp);
    free(v_temp);
    return (real_t)0;
}

PB_MAIN(kernel_k42)
