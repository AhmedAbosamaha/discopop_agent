#include "data.h"

real_t kernel_s318(void)
{
    int k, index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        index = 0;
        max = ABS(a[0]);

        /* Parallel pass: find the maximum absolute value */
        #pragma omp parallel for reduction(max:max) private(k)
        for (int i = 1; i < LEN_1D; i++) {
            k = inc * i;
            max = fmax(max, ABS(a[k]));
        }

        /* Serial pass: find the index of the first occurrence of the maximum */
        for (int i = 1; i < LEN_1D; i++) {
            k = inc * i;
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
