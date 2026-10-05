#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        j = -1;
        #pragma omp parallel for schedule(static) shared(a) reduction(max:j)
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0. && i > j) {
                j = i;
            }
        }
        chksum = (real_t) j;
        dummy(a, b, c, d, e);
    }
    return j+1;
}
