#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    #pragma omp parallel for private(chksum) lastprivate(j) 
    for (int nl = 0; nl < iterations; nl++) {
        int last_neg_index = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                last_neg_index = i;
            }
        }
        j = last_neg_index;
        chksum = (real_t) j;
        dummy(a, b, c, d, e);
    }
    return j+1;
}
