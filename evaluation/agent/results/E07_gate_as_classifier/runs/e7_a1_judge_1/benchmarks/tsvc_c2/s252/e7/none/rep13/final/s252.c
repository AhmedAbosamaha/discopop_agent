#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    real_t *products = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute all products (Do-All: no loop-carried dependences)
        for (int i = 0; i < LEN_1D; i++) {
            products[i] = b[i] * c[i];
        }

        // Phase 2: Compute sums using products
        real_t t = (real_t) 0.;
        for (int i = 0; i < LEN_1D; i++) {
            real_t s = products[i];
            a[i] = s + t;
            t = s;
        }

        dummy(a, b, c, d, e);
    }

    free(products);
    return (real_t)0;
}
