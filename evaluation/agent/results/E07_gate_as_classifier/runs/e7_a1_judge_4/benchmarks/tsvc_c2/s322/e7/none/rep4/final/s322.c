#include "data.h"
#include <stdlib.h>

real_t kernel_s322(void)
{
    real_t *a_temp = (real_t*) malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Compute phase: read from a (unmodified) and write to a_temp
        // No loop-carried dependence: each iteration reads different elements and writes to different elements
        for (int i = 2; i < LEN_1D; i++) {
            a_temp[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
        }
        // Write-back phase: copy computed values back to a
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a_temp[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_temp);
    return (real_t)0;
}
