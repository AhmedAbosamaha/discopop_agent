#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s112(void)
{
    real_t *temp_a = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Save original values of a before the loop
        memcpy(temp_a, a, LEN_1D * sizeof(real_t));

        // Parallelize the shift operation: each iteration reads from saved snapshot
        // and writes to a unique location, making iterations independent
        #pragma omp parallel for shared(a, b, temp_a)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i+1] = temp_a[i] + b[i];
        }

        dummy(a, b, c, d, e);
    }

    free(temp_a);
    return (real_t)0;
}
