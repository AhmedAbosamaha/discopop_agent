#include "data.h"
#include <stdlib.h>

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_vals = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *v_vals = (real_t *)malloc(LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_vals[i] = u[ku[i]];
            v_vals[i] = v[kv[i]];
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_vals[i] * c[i];
            v[jv[i]] = u_vals[i] * d[i] + c[i];
        }

        free(u_vals);
        free(v_vals);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
