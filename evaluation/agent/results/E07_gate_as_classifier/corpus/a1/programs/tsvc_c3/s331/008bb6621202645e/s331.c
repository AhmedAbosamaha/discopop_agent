#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        int j_prev = j;
        int j_local = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j_local = i;
            }
        }
        chksum = (real_t) j_local;
        dummy(a, b, c, d, e, chksum);
        j = j_local + (j_prev - j_prev);  /* Use j_prev to create loop-carried dependence */
    }
    return j+1;
}
