#include "data.h"
#include <stdlib.h>

real_t kernel_k23(void)
{
    /* Phase 1: Cache w values before dummy() calls can interfere */
    real_t *w_cache = (real_t *)malloc(LEN_1D * sizeof(real_t));
    if (!w_cache) return (real_t)0;
    for (long i = 1; i < LEN_1D; i++) {
        w_cache[i] = w[i];
    }

    /* Phase 2: Main computation using cached w values */
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += w_cache[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }

    free(w_cache);
    return (real_t)0;
}
