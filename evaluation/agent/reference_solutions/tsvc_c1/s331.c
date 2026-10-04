#include "data.h"

real_t kernel_s331(void)
{
    int j = -1;
    real_t chksum = 0;
    j = -1;
    #pragma omp parallel for reduction(max:j)
    for (int i = 0; i < LEN_1D; i++) {
        if (a[i] < (real_t)0.) {
            if (i > j) j = i;
        }
    }
    chksum = (real_t) j;
    (void)chksum;
    return j+1;
}
