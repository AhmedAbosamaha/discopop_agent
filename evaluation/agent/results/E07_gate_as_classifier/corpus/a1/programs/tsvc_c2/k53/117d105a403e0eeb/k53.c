#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *v_snapshot = malloc(sizeof(real_t) * LEN_1D);
        memcpy(v_snapshot, v, sizeof(real_t) * LEN_1D);

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_snapshot[kv[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }

        free(v_snapshot);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
