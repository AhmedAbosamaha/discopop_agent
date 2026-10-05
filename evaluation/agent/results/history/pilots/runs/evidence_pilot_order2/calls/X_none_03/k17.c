#include "evk/k17.h"

static real_t kernel_k17(void)
{
    real_t *u_updates = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *v_updates = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (long i = 0; i < LEN_1D; i++) {
        u_updates[i] = (real_t)0;
        v_updates[i] = (real_t)0;
    }

    for (long i = 1; i < LEN_1D; i++) {
        u_updates[ju[i]] += v[kv[i]] * c[i];
        v_updates[jv[i]] += u[ku[i]] * d[i];
    }

    for (long i = 0; i < LEN_1D; i++) {
        u[i] += u_updates[i];
        v[i] += v_updates[i];
    }

    free(u_updates);
    free(v_updates);
    return (real_t)0;
}

PB_MAIN(kernel_k17)
