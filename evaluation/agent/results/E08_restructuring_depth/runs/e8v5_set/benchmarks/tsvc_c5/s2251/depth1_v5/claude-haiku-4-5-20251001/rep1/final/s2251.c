#include "data.h"

real_t kernel_s2251(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            real_t s = (i == 0) ? (real_t)0.0 : (b[i-1]+c[i-1]);
            a[i] = s*e[i];
        }
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = a[i]+d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
