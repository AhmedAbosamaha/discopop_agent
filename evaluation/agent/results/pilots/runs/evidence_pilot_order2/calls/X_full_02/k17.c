#include "evk/k17.h"

static real_t kernel_k17(void)
{
    real_t *v_read = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    for (long i = 0; i < LEN_1D; i++) {
        v_read[i] = v[i];
    }

    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v_read[kv[i]] * c[i];
        v[jv[i]] += u[ku[i]] * d[i];
    }

    free(v_read);
    return (real_t)0;
}

PB_MAIN(kernel_k17)
