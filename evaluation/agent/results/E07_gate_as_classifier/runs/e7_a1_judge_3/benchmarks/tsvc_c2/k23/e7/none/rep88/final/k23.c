#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k23(void)
{
    real_t *c_snapshot = malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        // Save c before the inner loop so reads within the loop are invariant
        memcpy(c_snapshot, c, sizeof(real_t) * LEN_1D);

        for (long i = 1; i < LEN_1D; i++) {
            u[i] += w[i] * c_snapshot[i];
            v[i] = x[i] * d[i] + c_snapshot[i];
        }
        dummy(a, b, c, d, e);
    }

    free(c_snapshot);
    return (real_t)0;
}
