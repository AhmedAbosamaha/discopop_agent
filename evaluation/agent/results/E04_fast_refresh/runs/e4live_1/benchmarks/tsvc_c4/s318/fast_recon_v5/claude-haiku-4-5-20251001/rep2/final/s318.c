#include "data.h"

real_t kernel_s318(void)
{
    int k, index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        k = 0;
        index = 0;
        max = ABS(a[0]);
        k += inc;
        real_t found_max = max;
        int found_index = index;

        #pragma omp parallel for reduction(max:found_max) 
        for (int i = 1; i < LEN_1D; i++) {
            found_max = fmax(found_max, ABS(a[i*inc]));
        }

        for (int i = 1; i < LEN_1D; i++) {
            if (ABS(a[i*inc]) == found_max) {
                found_index = i;
            }
        }

        max = found_max;
        index = found_index;
        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
