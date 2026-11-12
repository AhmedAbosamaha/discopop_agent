#include "data.h"

real_t kernel_s331(void)
{
    int final_j;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        int j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        final_j = j;
        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }
    return final_j + 1;
}
