#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    real_t *chksum_values = (real_t *)malloc(iterations * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        chksum_values[nl] = (real_t) j;
    }
    for (int nl = 0; nl < iterations; nl++) {
        chksum = chksum_values[nl];
        dummy(a, b, c, d, e, chksum);
    }
    free(chksum_values);
    return j+1;
}
