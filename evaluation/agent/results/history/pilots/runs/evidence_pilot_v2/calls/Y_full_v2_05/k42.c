#include "evk/k42.h"

static real_t kernel_k42(void)
{
    real_t *u_snap = (real_t*)malloc(LEN_1D * sizeof(real_t));
    real_t *v_snap = (real_t*)malloc(LEN_1D * sizeof(real_t));
    memcpy(u_snap, u, LEN_1D * sizeof(real_t));
    memcpy(v_snap, v, LEN_1D * sizeof(real_t));

    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v_snap[kv[i]] * c[i];
        v[jv[i]] += u_snap[ku[i]] * d[i];
    }

    free(u_snap);
    free(v_snap);
    return (real_t)0;
}

PB_MAIN(kernel_k42)
