#include "evk/k17.h"

static real_t kernel_k17(void)
{
    real_t *u_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *v_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (long i = 0; i < LEN_1D; i++) {
        u_copy[i] = u[i];
        v_copy[i] = v[i];
    }

    for (long i = 1; i < LEN_1D; i++) {
        u_copy[ju[i]] += v[kv[i]] * c[i];
        v_copy[jv[i]] += u[ku[i]] * d[i];
    }

    for (long i = 0; i < LEN_1D; i++) {
        u[i] = u_copy[i];
        v[i] = v_copy[i];
    }

    free(u_copy);
    free(v_copy);

    return (real_t)0;
}

PB_MAIN(kernel_k17)
