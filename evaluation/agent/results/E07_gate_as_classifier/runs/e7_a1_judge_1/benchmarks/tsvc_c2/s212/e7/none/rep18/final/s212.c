#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Save original a values to break loop-carried dependence on a[i+1]
        real_t *a_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(a_copy, a, LEN_1D * sizeof(real_t));

        #pragma omp parallel for shared(a_copy) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_copy[i] * c[i];
            b[i] += a_copy[i + 1] * d[i];
        }

        free(a_copy);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
