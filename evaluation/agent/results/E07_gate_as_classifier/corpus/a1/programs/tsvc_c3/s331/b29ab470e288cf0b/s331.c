#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int *j_vals = (int *)malloc(iterations * sizeof(int));
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        j_vals[nl] = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j_vals[nl] = i;
            }
        }
        chksum = (real_t) j_vals[nl];
        dummy(a, b, c, d, e, chksum);
    }
    int j = j_vals[iterations - 1];
    free(j_vals);
    return j+1;
}
