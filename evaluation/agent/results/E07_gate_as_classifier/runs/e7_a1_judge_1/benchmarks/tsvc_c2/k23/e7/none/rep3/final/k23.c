#include <stdlib.h>
#include "data.h"

real_t kernel_k23(void)
{
    real_t *c_snapshot = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *w_snapshot = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Snapshot c and w before the inner loop to break loop-carried dependences
        for (long i = 1; i < LEN_1D; i++) {
            c_snapshot[i] = c[i];
            w_snapshot[i] = w[i];
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[i] += w_snapshot[i] * c_snapshot[i];
            v[i] = x[i] * d[i] + c_snapshot[i];
        }
        dummy(a, b, c, d, e);
    }

    free(c_snapshot);
    free(w_snapshot);
    return (real_t)0;
}
