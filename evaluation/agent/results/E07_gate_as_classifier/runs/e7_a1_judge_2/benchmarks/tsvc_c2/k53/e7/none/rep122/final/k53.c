#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k53(void)
{
    real_t *v_prev = (real_t *)malloc(LEN_1D * sizeof(real_t));
    memcpy(v_prev, v, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_prev[kv[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        memcpy(v_prev, v, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }
    free(v_prev);
    return (real_t)0;
}
