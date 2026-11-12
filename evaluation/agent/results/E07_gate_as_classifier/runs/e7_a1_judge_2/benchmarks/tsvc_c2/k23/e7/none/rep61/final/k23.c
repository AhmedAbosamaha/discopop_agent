#include "data.h"
#include <stdlib.h>

real_t kernel_k23(void)
{
    real_t *w_new = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: read from current w, compute u and new w values
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += w[i] * c[i];
            w_new[i] = x[i] * d[i] + c[i];
        }
        // Phase 2: write new w values back
        for (long i = 1; i < LEN_1D; i++) {
            w[i] = w_new[i];
        }
        dummy(a, b, c, d, e);
    }

    free(w_new);
    return (real_t)0;
}
