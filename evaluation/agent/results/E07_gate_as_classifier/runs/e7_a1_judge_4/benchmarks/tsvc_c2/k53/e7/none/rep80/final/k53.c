#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k53(void)
{
    real_t *v_old = malloc(LEN_1D * sizeof(real_t));
    memcpy(v_old, v, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_old[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
            v_old[jv[i]] = v[jv[i]];
        }
        dummy(a, b, c, d, e);
    }

    free(v_old);
    return (real_t)0;
}
