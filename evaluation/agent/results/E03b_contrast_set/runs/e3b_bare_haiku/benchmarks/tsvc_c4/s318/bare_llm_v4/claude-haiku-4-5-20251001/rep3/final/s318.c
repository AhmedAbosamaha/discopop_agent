#include "data.h"

real_t kernel_s318(void)
{
    int k, index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: find maximum absolute value in parallel using reduction
        real_t initial_max = ABS(a[0]);
        max = initial_max;
        #pragma omp parallel for reduction(max:max)
        for (int i = 1; i < LEN_1D; i++) {
            real_t abs_val = ABS(a[i*inc]);
            max = (abs_val > max) ? abs_val : max;
        }

        // Second pass: find index of first element strictly greater than initial_max
        index = 0;
        for (int i = 1; i < LEN_1D; i++) {
            if (ABS(a[i*inc]) > initial_max) {
                index = i;
                break;
            }
        }

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
