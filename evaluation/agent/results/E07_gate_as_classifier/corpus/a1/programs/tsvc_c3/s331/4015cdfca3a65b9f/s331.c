#include "data.h"

real_t kernel_s331(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        j = -1;
        #pragma omp parallel for lastprivate(j) 
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        real_t chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }
    return j+1;
}
