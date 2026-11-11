#include "data.h"
#include <stdlib.h>

real_t kernel_k19(void)
{
    real_t *u_read = malloc(sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            u_read[i] = u[ku[i]];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u_read[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(u_read);
    return (real_t)0;
}
