#include "data.h"

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t s_array[LEN_1D];
        real_t t_array[LEN_1D];

        // Loop 1: Compute s values - Do-All (no dependence)
        for (int i = 0; i < LEN_1D; i++) {
            s_array[i] = b[i] * c[i];
        }

        // Loop 2: Compute cumulative t values - Sequential (loop-carried on t)
        real_t t = (real_t) 0.;
        for (int i = 0; i < LEN_1D; i++) {
            t_array[i] = t;
            t = s_array[i];
        }

        // Loop 3: Compute a values - Do-All (no dependence, reads precomputed arrays)
        #pragma omp parallel for firstprivate(s_array,t_array) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_array[i] + t_array[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
