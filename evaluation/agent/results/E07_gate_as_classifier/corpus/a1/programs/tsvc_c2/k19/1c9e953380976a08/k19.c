#include <stdlib.h>
#include <string.h>
#include "data.h"

real_t kernel_k19(void)
{
    real_t *u_delta = calloc(LEN_1D, sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        memset(u_delta, 0, LEN_1D * sizeof(real_t));
        for (long i = 1; i < LEN_1D; i++) {
            u_delta[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = (u[ku[i]] + u_delta[ku[i]]) * d[i] + c[i];
        }
        for (long j = 0; j < LEN_1D; j++) {
            u[j] += u_delta[j];
        }
        dummy(a, b, c, d, e);
    }
    free(u_delta);
    return (real_t)0;
}
