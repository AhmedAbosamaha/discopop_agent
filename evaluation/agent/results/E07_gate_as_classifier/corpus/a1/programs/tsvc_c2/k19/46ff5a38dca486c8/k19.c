#include "data.h"
#include <stdlib.h>

real_t kernel_k19(void)
{
    real_t *temp_u = malloc(LEN_1D * sizeof(real_t));
    real_t *temp_v = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            temp_u[i] = v[kv[i]] * c[i];
            temp_v[i] = u[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += temp_u[i];
            v[jv[i]] = temp_v[i];
        }
        dummy(a, b, c, d, e);
    }

    free(temp_u);
    free(temp_v);
    return (real_t)0;
}
