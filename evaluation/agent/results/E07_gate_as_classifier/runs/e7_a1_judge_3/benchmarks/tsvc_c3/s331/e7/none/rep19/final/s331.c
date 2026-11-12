#include "data.h"

real_t kernel_s331(void)
{
    int j = -1;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }
    return j+1;
}
