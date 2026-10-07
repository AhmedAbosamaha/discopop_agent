#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        int jm = -1;
        #pragma omp parallel for default(none) shared(a) reduction(max:jm) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0. && i > jm) {
                jm = i;
            }
        }
        j = jm;
        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }
    return j+1;
}
