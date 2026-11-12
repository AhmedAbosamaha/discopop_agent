#include "data.h"

real_t kernel_s252(void)
{
    real_t t;
    for (int nl = 0; nl < iterations; nl++) {
        real_t s_array[LEN_1D];

        // Compute s values: Do-All loop with no loop-carried dependence
        #pragma omp parallel for lastprivate(s_array) 
        for (int i = 0; i < LEN_1D; i++) {
            s_array[i] = b[i] * c[i];
        }

        // Compute cumulative a values: sequential prefix computation
        t = (real_t) 0.;
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_array[i] + t;
            t = s_array[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
