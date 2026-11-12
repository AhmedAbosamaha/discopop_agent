#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k23(void)
{
    real_t *c_snapshot = malloc(LEN_1D * sizeof(real_t));
    memcpy(c_snapshot, c, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += w[i] * c_snapshot[i];
            v[i] = x[i] * d[i] + c_snapshot[i];
        }
        dummy(a, b, c, d, e);
        memcpy(c_snapshot, c, LEN_1D * sizeof(real_t));
    }

    free(c_snapshot);
    return (real_t)0;
}
