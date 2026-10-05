#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    real_t *products = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute products b[i] * c[i] in parallel
        // Each iteration is independent; threads write to disjoint elements
        #pragma omp parallel for shared(b, c, products)
        for (int i = 0; i < LEN_1D; i++) {
            products[i] = b[i] * c[i];
        }

        // Phase 2: Set a[0] = products[0] (single-threaded setup)
        a[0] = products[0];

        // Phase 3: Compute a[i] = products[i] + products[i-1] in parallel
        // Each iteration depends only on array reads from products, not on other a values
        // No iteration depends on another iteration's write to a
        #pragma omp parallel for shared(a, products)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = products[i] + products[i-1];
        }

        dummy(a, b, c, d, e);
    }

    free(products);
    return (real_t)0;
}
