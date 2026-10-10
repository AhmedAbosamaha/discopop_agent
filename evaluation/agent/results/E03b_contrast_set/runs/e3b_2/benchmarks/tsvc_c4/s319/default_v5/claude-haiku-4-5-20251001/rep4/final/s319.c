#include "data.h"

real_t kernel_s319(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute and write array values
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = c[i] + d[i];
            b[i] = c[i] + e[i];
        }

        // Phase 2: Accumulate sum from arrays
        sum = 0.;
        #pragma omp parallel for reduction(+:sum) 
        for (int i = 0; i < LEN_1D; i++) {
            sum += a[i] + b[i];
        }

        dummy(a, b, c, d, e, sum);
    }
    return sum;
}
