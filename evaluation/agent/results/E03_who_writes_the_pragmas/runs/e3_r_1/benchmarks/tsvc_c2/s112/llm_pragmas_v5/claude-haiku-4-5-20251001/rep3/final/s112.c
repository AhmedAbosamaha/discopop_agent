#include "data.h"
#include <stdlib.h>

real_t kernel_s112(void)
{
    real_t *a_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Copy current state of a into temporary buffer to stabilize the read set
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) {
            a_temp[i] = a[i];
        }

        // Compute in parallel, reading from stable buffer to break inter-iteration dependence
        #pragma omp parallel for
        for (int i = LEN_1D - 2; i >= 0; i--) {
            a[i+1] = a_temp[i] + b[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_temp);
    return (real_t)0;
}
