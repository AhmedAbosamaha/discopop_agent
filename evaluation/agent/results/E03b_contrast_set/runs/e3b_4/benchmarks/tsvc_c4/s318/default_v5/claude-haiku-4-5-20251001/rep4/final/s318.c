#include "data.h"
#include <stdlib.h>

real_t kernel_s318(void)
{
    int index;
    real_t max, chksum;

    real_t *vals = malloc((LEN_1D - 1) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        index = 0;
        max = ABS(a[0]);

        #pragma omp parallel for shared(vals) 
        for (int i = 1; i < LEN_1D; i++) {
            int k = i * inc;
            vals[i - 1] = ABS(a[k]);
        }

        for (int i = 0; i < LEN_1D - 1; i++) {
            if (vals[i] > max) {
                max = vals[i];
                index = i + 1;
            }
        }

        chksum = max + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }

    free(vals);
    return max + index + 1;
}
