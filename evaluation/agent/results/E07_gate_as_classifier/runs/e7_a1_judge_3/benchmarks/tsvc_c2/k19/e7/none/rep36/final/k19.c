#include <stdlib.h>
#include <string.h>
#include "data.h"

real_t kernel_k19(void)
{
    real_t *u_swap = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(u_swap, u, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u_swap[ku[i]] * d[i] + c[i];
        }

        dummy(a, b, c, d, e);
    }

    free(u_swap);
    return (real_t)0;
}
