#include "data.h"
#include <stdlib.h>

real_t kernel_k53(void)
{
    real_t *v_new = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v_new[i] = u[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = v_new[i];
        }
        dummy(a, b, c, d, e);
    }

    free(v_new);
    return (real_t)0;
}
