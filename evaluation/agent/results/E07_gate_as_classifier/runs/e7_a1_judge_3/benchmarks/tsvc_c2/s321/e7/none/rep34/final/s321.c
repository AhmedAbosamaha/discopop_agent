#include "data.h"

real_t kernel_s321(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t temp[LEN_1D];
        #pragma omp parallel for lastprivate(temp) 
        for (int i = 0; i < LEN_1D; i++) {
            temp[i] = a[i];
        }
        for (int i = 1; i < LEN_1D; i++) {
            temp[i] += temp[i-1] * b[i];
        }
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = temp[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
