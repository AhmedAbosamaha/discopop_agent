#include "data.h"

real_t kernel_s331(void)
{
    int j = -1;
    real_t chksum;
    real_t a_prev = a[0];
    for (int nl = 0; nl < iterations; nl++) {
        volatile real_t _a_check = a_prev;
        int j_local = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j_local = i;
            }
        }
        chksum = (real_t) j_local;
        dummy(a, b, c, d, e, chksum);
        a_prev = a[0];
        j = j_local;
    }
    return j+1;
}
