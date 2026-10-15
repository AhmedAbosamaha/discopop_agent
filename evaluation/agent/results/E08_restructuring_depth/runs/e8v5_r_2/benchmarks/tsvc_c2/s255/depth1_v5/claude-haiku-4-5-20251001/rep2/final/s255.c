#include "data.h"

real_t kernel_s255(void)
{
    real_t x, y;
    // Compute a for iteration 0 using initial b
    #pragma omp parallel for 
    for (int i = 0; i < LEN_1D; i++) {
        real_t x_local = (i > 0) ? b[i-1] : b[LEN_1D-1];
        real_t y_local = (i > 1) ? b[i-2] : ((i == 1) ? b[LEN_1D-1] : b[LEN_1D-2]);
        a[i] = (b[i] + x_local + y_local) * (real_t).333;
    }
    // Pipeline: interleave dummy calls with computation of subsequent iterations
    for (int nl = 0; nl < iterations - 1; nl++) {
        // Update b via dummy (for next iteration's computation)
        dummy(a, b, c, d, e);
        // Compute a for iteration nl+1 using updated b
 #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            real_t x_local = (i > 0) ? b[i-1] : b[LEN_1D-1];
            real_t y_local = (i > 1) ? b[i-2] : ((i == 1) ? b[LEN_1D-1] : b[LEN_1D-2]);
            a[i] = (b[i] + x_local + y_local) * (real_t).333;
        }
    }
    // Final dummy call for the last iteration
    dummy(a, b, c, d, e);
    return (real_t)0;
}
