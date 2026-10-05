#include "evk/k42.h"

static real_t kernel_k42(void)
{
    real_t *u_new = malloc(LEN_1D * sizeof(real_t));
    real_t *v_new = malloc(LEN_1D * sizeof(real_t));

    memcpy(u_new, u, LEN_1D * sizeof(real_t));
    memcpy(v_new, v, LEN_1D * sizeof(real_t));

    for (long i = 1; i < LEN_1D; i++) {
        u_new[ju[i]] += v[kv[i]] * c[i];
        v_new[jv[i]] += u[ku[i]] * d[i];
    }

    memcpy(u, u_new, LEN_1D * sizeof(real_t));
    memcpy(v, v_new, LEN_1D * sizeof(real_t));

    free(u_new);
    free(v_new);

    return (real_t)0;
}

PB_MAIN(kernel_k42)
