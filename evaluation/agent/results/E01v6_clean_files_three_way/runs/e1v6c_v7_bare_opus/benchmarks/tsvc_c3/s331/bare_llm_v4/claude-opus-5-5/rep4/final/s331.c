#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        int jmax = -1;
        #pragma omp parallel for shared(a)reduction(max:jmax) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0. && i > jmax) {
                jmax = i;
            }
        }
        j = jmax;
        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }
    return j+1;
}
