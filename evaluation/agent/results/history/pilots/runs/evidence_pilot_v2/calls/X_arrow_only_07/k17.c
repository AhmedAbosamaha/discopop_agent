#include "evk/k17.h"

static real_t kernel_k17(void)
{
    real_t *v_snapshot = (real_t *)malloc(LEN_1D * sizeof(real_t));
    memcpy(v_snapshot, v, LEN_1D * sizeof(real_t));

    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v_snapshot[kv[i]] * c[i];
        v[jv[i]] += u[ku[i]] * d[i];
    }

    free(v_snapshot);
    return (real_t)0;
}

PB_MAIN(kernel_k17)
