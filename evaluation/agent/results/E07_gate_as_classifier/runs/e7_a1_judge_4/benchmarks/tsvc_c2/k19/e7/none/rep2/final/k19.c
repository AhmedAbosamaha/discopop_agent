#include "data.h"

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_tmp = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (long i = 0; i < LEN_1D; i++) u_tmp[i] = u[i];
        for (long i = 1; i < LEN_1D; i++) {
            u_tmp[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u_tmp[ku[i]] * d[i] + c[i];
        }
        for (long i = 0; i < LEN_1D; i++) u[i] = u_tmp[i];
        free(u_tmp);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
