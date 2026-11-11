#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;

    j = -1;
    for (int i = 0; i < LEN_1D; i++) {
        if (a[i] < (real_t)0.) {
            j = i;
        }
    }
    chksum = (real_t) j;

    for (int nl = 0; nl < iterations; nl++) {
        dummy(a, b, c, d, e, chksum);
    }

    return j+1;
}
