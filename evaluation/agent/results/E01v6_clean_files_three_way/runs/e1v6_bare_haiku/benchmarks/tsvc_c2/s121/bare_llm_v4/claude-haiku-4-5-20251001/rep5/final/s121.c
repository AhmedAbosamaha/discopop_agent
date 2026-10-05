#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    int j;
    real_t *a_temp = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Parallel inner loop: compute a_temp[i] = a[i+1] + b[i]
        // No loop-carried dependence: each iteration writes to a unique a_temp[i]
        // and reads from a[i+1] and b[i] without conflicts
        #pragma omp parallel for private(j)
        for (int i = 0; i < LEN_1D-1; i++) {
            j = i + 1;
            a_temp[i] = a[j] + b[i];
        }

        // Copy results back to a (sequential - small constant work)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_temp[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_temp);
    return (real_t)0;
}
