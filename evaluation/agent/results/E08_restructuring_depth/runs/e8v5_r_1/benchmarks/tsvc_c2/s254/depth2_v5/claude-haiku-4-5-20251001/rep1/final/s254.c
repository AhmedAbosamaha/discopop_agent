#include "data.h"

real_t kernel_s254(void)
{
    // Compute a for the first iteration
    a[0] = (b[0] + b[LEN_1D - 1]) * (real_t).5;
    #pragma omp parallel for 
    for (int i = 1; i < LEN_1D; i++) {
        a[i] = (b[i] + b[i - 1]) * (real_t).5;
    }

    // Pipeline: each iteration applies dummy (modifying b), then computes a for next iteration
    for (int nl = 0; nl < iterations - 1; nl++) {
        dummy(a, b, c, d, e);
        a[0] = (b[0] + b[LEN_1D - 1]) * (real_t).5;
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i - 1]) * (real_t).5;
        }
    }

    // Apply dummy for the final iteration
    dummy(a, b, c, d, e);

    return (real_t)0;
}
