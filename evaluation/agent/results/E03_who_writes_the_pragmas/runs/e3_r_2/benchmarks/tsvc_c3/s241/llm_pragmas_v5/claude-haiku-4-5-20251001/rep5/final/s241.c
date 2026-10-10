#include "data.h"
#include <stdlib.h>

real_t kernel_s241(void)
{
    real_t *a_saved = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Save current a values before overwriting (original a[i+1] needed in second loop)
        #pragma omp parallel for shared(a, a_saved)
        for (int i = 0; i < LEN_1D; i++) {
            a_saved[i] = a[i];
        }

        // Compute new a values — no loop-carried dependence on a
        #pragma omp parallel for shared(a, b, c, d)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
        }

        // Compute b values using new a[i] but old a[i+1] — no loop-carried dependence
        #pragma omp parallel for shared(a, b, c, d, a_saved)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = a[i] * a_saved[i+1] * d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_saved);
    return (real_t)0;
}
