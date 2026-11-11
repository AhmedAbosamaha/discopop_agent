#include "data.h"
#include <stdlib.h>

real_t kernel_s241(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Save the current a values before modifying them
        real_t *old_a = (real_t *)malloc(sizeof(real_t) * LEN_1D);
        for (int i = 0; i < LEN_1D; i++) {
            old_a[i] = a[i];
        }

        // Phase 1: Compute all new a[i] values
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
        }

        // Phase 2: Compute all new b[i] values using new a[i] and old a[i+1]
        #pragma omp parallel for shared(old_a) 
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = a[i] * old_a[i+1] * d[i];
        }

        free(old_a);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
