#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int *j_values = (int *)malloc(iterations * sizeof(int));

    // Pass 1: Read from a and compute j for each iteration (Do-All loop)
    for (int nl = 0; nl < iterations; nl++) {
        int j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        j_values[nl] = j;
    }

    // Pass 2: Call dummy with computed values
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        chksum = (real_t) j_values[nl];
        dummy(a, b, c, d, e, chksum);
    }

    int j = j_values[iterations - 1];
    free(j_values);
    return j+1;
}
