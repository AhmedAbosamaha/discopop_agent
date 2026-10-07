#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        j = -1;
        #pragma omp parallel shared(j)
        {
            int local_j = -1;
            #pragma omp for
            for (int i = 0; i < LEN_1D; i++) {
                if (a[i] < (real_t)0.) {
                    local_j = i;
                }
            }
            #pragma omp critical
            {
                if (local_j > j) j = local_j;
            }
        }
        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }
    return j+1;
}
