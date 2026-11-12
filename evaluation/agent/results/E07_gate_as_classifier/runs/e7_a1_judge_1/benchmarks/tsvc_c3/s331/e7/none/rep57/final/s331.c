#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        int found_last_negative = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                found_last_negative = i;
            }
        }
        j = found_last_negative;
        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }
    return j+1;
}
