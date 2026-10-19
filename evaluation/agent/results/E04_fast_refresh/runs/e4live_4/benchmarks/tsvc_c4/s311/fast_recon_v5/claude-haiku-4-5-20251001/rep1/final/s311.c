#include "data.h"

real_t kernel_s311(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t sum = (real_t)0.;
        #pragma omp parallel for reduction(+:sum) 
        for (int i = 0; i < LEN_1D; i++) {
            sum += a[i];
        }
        dummy(a, b, c, d, e, sum);
    }
    return (real_t)0;
}
