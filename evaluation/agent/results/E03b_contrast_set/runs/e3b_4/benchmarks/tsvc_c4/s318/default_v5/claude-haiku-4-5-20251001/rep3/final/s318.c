#include "data.h"
#include <stdlib.h>

real_t kernel_s318(void)
{
    int index;
    real_t max, chksum;
    for (int nl = 0; nl < iterations; nl++) {
        index = 0;
        max = ABS(a[0]);

        real_t* abs_vals = (real_t*)malloc(LEN_1D * sizeof(real_t));
        abs_vals[0] = max;

        #pragma omp parallel for shared(abs_vals) 
        for (int i = 1; i < LEN_1D; i++) {
            abs_vals[i] = ABS(a[i * inc]);
        }

        for (int i = 1; i < LEN_1D; i++) {
            if (abs_vals[i] > max) {
                index = i;
                max = abs_vals[i];
            }
        }

        free(abs_vals);
        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }
    return max + index + 1;
}
