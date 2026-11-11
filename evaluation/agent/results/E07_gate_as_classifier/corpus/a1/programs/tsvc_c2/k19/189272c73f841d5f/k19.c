#include "data.h"
#include <stdlib.h>

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_delta = malloc(LEN_1D * sizeof(real_t));
        real_t *v_new = malloc(LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_delta[i] = v[kv[i]] * c[i];
            v_new[i] = u[ku[i]] * d[i] + c[i];
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += u_delta[i];
            v[jv[i]] = v_new[i];
        }

        free(u_delta);
        free(v_new);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
