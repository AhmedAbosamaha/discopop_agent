#include "data.h"

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute new v values (line 8, independent iterations)
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u[i + far] * d[i] + c[i];
        }

        // Phase 2: Update u using new v values (line 7, independent iterations)
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
