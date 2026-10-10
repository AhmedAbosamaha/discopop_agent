#include "data.h"
#include <stdlib.h>

real_t kernel_k53(void)
{
    real_t *u_delta = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(u_delta) 
        for (long i = 0; i < LEN_1D; i++) {
            u_delta[i] = 0.0;
        }
        for (long i = 1; i < LEN_1D; i++) {
            u_delta[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = (u[ku[i]] + u_delta[ku[i]]) * d[i] + c[i];
        }
        for (long i = 0; i < LEN_1D; i++) {
            u[i] += u_delta[i];
        }
        dummy(a, b, c, d, e);
    }
    free(u_delta);
    return (real_t)0;
}
