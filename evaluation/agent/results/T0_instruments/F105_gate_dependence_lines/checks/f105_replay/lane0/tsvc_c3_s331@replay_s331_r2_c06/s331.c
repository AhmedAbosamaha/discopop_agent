#include "data.h"

real_t kernel_s331(void)
{
    int j = -1;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        int j_local = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j_local = i;
            }
        }
        chksum = (real_t) j_local;
        dummy(a, b, c, d, e, chksum);
        j = j_local;
    }
    return j+1;
}
