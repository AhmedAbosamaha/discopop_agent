#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k53(void)
{
    real_t *v_snapshot = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    memcpy(v_snapshot, v, sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_snapshot[kv[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        memcpy(v_snapshot, v, sizeof(real_t) * LEN_1D);
        dummy(a, b, c, d, e);
    }

    free(v_snapshot);
    return (real_t)0;
}
