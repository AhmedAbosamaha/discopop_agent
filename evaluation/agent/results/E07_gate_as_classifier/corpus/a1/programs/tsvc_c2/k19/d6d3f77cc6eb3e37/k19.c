#include "data.h"

real_t kernel_k19(void)
{
    real_t *temp = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            temp[i] = u[ku[i]];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = temp[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(temp);
    return (real_t)0;
}
