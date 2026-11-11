#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k53(void)
{
    real_t *v_snap = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(v_snap, v, sizeof(real_t) * LEN_1D);

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_snap[kv[i]] * c[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(v_snap);
    return (real_t)0;
}
