#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    real_t chksum;
    int j_final = -1;
    for (int nl = 0; nl < iterations; nl++) {
        int j = -1;
        #pragma omp parallel for lastprivate(j) 
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
        j_final = j;
    }
    return j_final+1;
}
