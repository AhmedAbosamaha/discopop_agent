#include "data.h"

real_t kernel_s318(void)
{
    int index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        max = ABS(a[0]);
        #pragma omp parallel for reduction(max:max) 
        for (int i = 1; i < LEN_1D; i++) {
            int k = i * inc;
            max = fmax(max, ABS(a[k]));
        }
        index = 0;
        for (int i = 1; i < LEN_1D; i++) {
            int k = i * inc;
            if (ABS(a[k]) == max) {
                index = i;
            }
        }
        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
