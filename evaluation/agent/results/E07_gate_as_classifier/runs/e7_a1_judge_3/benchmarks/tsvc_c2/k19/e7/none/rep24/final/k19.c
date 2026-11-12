#include "data.h"
#include <stdlib.h>

real_t kernel_k19(void)
{
    real_t *u_save = malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            u_save[i] = u[ku[i]];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u_save[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(u_save);
    return (real_t)0;
}
