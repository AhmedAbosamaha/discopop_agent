#include "data.h"

real_t kernel_s313(void)
{
    real_t dot;
    for (int nl = 0; nl < iterations; nl++) {
        real_t local_dot = (real_t)0.;
        #pragma omp parallel for reduction(+:local_dot) 
        for (int i = 0; i < LEN_1D; i++) {
            local_dot += a[i] * b[i];
        }
        dot = local_dot;
        dummy(a, b, c, d, e, dot);
    }
    return dot;
}
