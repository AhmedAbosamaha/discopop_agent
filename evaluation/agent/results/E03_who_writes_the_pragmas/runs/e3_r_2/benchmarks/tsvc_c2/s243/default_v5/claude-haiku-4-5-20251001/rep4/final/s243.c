#include "data.h"
#include <stdlib.h>

real_t kernel_s243(void)
{
    // Allocate once outside the loop to minimize overhead
    real_t *a_next = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Snapshot a[i+1] before the loop to break the backward dependence
        #pragma omp parallel for shared(a_next) 
        for (int i = 0; i < LEN_1D - 1; i++) {
            a_next[i] = a[i + 1];
        }

        #pragma omp parallel for shared(a_next) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_next[i] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_next);
    return (real_t)0;
}
