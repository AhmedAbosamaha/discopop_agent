#include "data.h"

real_t kernel_s341(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: mark positive elements directly in a (no dependence on j - parallelizable)
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[i] = b[i];
            } else {
                a[i] = -(real_t)1.0;  // sentinel: will be skipped by condition in second pass
            }
        }
        // Second pass: compact selected values within a
        j = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] > (real_t)0.) {
                a[j] = a[i];
                j++;
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
