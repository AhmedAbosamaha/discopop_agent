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
    return j+1;
}
