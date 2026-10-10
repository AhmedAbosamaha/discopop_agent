#include "data.h"

real_t kernel_s318(void)
{
    int k, index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        index = 0;
        max = ABS(a[0]);

        /* Parallel pass: find maximum value using reduction.
           k is private and computed as k = i * inc, removing the loop-carried
           increment dependency. Each thread maintains its own max and combines
           at the end of the parallel region. */
        #pragma omp parallel for private(k) reduction(max:max)
        for (int i = 1; i < LEN_1D; i++) {
            k = i * inc;
            if (ABS(a[k]) > max) {
                max = ABS(a[k]);
            }
        }

        /* Sequential pass: find the index of the first element equal to max.
           The reduction guarantees max is one of the computed values, so == is safe. */
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
