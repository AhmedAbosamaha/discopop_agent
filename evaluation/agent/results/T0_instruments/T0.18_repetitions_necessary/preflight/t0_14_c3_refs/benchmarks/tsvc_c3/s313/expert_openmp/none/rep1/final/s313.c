#include "data.h"

real_t kernel_s313(void)
{
    real_t dot = 0;
    for (int nl = 0; nl < iterations; nl++) {
        dot = (real_t)0.;
        #pragma omp parallel for reduction(+:dot)
        for (int i = 0; i < LEN_1D; i++) dot += a[i] * b[i];
        dummy(a, b, c, d, e, dot);
    }
    return dot;
}
