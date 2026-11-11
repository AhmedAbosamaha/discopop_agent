#include "data.h"
#include <stdlib.h>

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_contrib = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (long i = 0; i < LEN_1D; i++) {
            u_contrib[i] = 0.0;
        }

        for (long i = 1; i < LEN_1D; i++) {
            u_contrib[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }

        for (long i = 0; i < LEN_1D; i++) {
            u[i] += u_contrib[i];
        }

        free(u_contrib);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
