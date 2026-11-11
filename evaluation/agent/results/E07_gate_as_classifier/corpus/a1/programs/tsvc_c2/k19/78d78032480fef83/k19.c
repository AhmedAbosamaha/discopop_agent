#include "data.h"
#include <stdlib.h>

real_t kernel_k19(void)
{
    real_t *u_delta = malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u_delta[i] = v[kv[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += u_delta[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(u_delta);
    return (real_t)0;
}
