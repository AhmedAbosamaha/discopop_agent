#include "data.h"
#include <stdlib.h>

real_t kernel_s321(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Snapshot array a to break loop-carried dependence
        real_t *a_prev = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (int i = 0; i < LEN_1D; i++) {
            a_prev[i] = a[i];
        }
        // Inner loop now reads from constant a_prev: Do-All pattern
        for (int i = 1; i < LEN_1D; i++) {
            a[i] += a_prev[i-1] * b[i];
        }
        free(a_prev);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
