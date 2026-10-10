#include "data.h"

real_t kernel_s319(void)
{
    real_t sum = 0;
    for (int nl = 0; nl < iterations; nl++) {
        sum = (real_t)0.;
        #pragma omp parallel for reduction(+:sum)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = c[i] + d[i];
            sum += a[i];
            b[i] = c[i] + e[i];
            sum += b[i];
        }
        dummy(a, b, c, d, e, sum);
    }
    return sum;
}
