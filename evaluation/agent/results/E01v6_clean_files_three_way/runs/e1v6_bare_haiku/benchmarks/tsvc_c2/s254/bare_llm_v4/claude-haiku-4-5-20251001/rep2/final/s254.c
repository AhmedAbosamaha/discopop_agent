#include "data.h"

real_t kernel_s254(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        x = b[LEN_1D-1];
        // Handle first element separately (uses initial x = b[LEN_1D-1])
        a[0] = (b[0] + x) * (real_t).5;
        // Parallel loop for remaining elements: each reads b[i-1] instead of scalar x
        // shared(a, b): a is written by parallel iterations to different elements;
        //               b is read by parallel iterations from different elements
        #pragma omp parallel for shared(a, b)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = (b[i] + b[i-1]) * (real_t).5;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
