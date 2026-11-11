#include "data.h"

real_t kernel_s331(void)
{
    real_t chksum;
    int final_j = -1;
    for (int nl = 0; nl < iterations; nl++) {
        int j = -1;
        int found = 0;
        for (int i = LEN_1D - 1; i >= 0; i--) {
            if (!found && a[i] < (real_t)0.) {
                j = i;
                found = 1;
            }
        }
        chksum = (real_t) j;
        dummy(a, b, c, d, e);
        final_j = j;
    }
    return final_j+1;
}
