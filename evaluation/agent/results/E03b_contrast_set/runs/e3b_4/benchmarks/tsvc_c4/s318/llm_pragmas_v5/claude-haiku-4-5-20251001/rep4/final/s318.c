#include "data.h"

real_t kernel_s318(void)
{
    int k, index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        index = 0;
        max = ABS(a[0]);

        // Parallel phase: find the maximum value across all elements
        // Dependencies removed by deriving k from i and using reduction for max
        #pragma omp parallel for private(k) reduction(max: max)
        for (int i = 1; i < LEN_1D; i++) {
            k = i * inc;
            real_t val = ABS(a[k]);
            if (val > max) {
                max = val;
            }
        }

        // Serial phase: find the index of the maximum value
        // This is a linear search with constant-factor overhead
        for (int i = 1; i < LEN_1D; i++) {
            k = i * inc;
            if (ABS(a[k]) == max) {
                index = i;
                break;
            }
        }

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
