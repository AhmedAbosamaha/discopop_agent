#include "data.h"

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Part 1: Update v using current u */
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u[i + far] * d[i] + c[i];
        }
        /* Part 2: Update u using new v */
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
