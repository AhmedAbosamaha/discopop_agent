#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        j = -1;
        #pragma omp parallel for reduction(max:j)
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        // Handle edge case: if no negative values found, reduction initializes j
        // to INT_MIN; reset to -1 if that occurred
        if (j < -1) j = -1;
        chksum = (real_t) j;
        dummy(a, b, c, d, e);
    }
    return j+1;
}
