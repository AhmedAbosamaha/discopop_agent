#include "data.h"
#include <stdlib.h>

real_t kernel_k23(void)
{
    real_t *w_local = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            w_local[i] = w[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[i] = u[i] + w_local[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(w_local);
    return (real_t)0;
}
