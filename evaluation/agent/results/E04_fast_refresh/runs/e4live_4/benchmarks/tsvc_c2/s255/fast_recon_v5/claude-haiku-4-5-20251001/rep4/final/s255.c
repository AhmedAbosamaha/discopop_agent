#include "data.h"

real_t kernel_s255(void)
{
    real_t x, y;
    for (int nl = 0; nl < iterations; nl++) {
        // Break loop-carried dependence on x and y by computing them locally per iteration
        // Original recurrence: x[i] = b[i-1], y[i] = b[i-2] (with wraparound)
        // Compute inline to avoid malloc/free and extra passes
 #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            real_t x = b[(i - 1 + LEN_1D) % LEN_1D];
            real_t y = b[(i - 2 + LEN_1D) % LEN_1D];
            a[i] = (b[i] + x + y) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
