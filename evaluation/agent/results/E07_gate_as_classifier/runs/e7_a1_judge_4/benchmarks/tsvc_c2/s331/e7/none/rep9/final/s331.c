#include "data.h"

real_t kernel_s331(void)
{
    real_t chksum;
    int j = -1;
    for (int nl = 0; nl < iterations; nl++) {
        j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        chksum = (real_t) j;
    }
    for (int nl = 0; nl < iterations; nl++) {
        dummy(a, b, c, d, e);
    }
    return j+1;
}
