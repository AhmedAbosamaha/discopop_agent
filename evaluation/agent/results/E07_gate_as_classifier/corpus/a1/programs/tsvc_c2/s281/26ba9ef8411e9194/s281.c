#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        // Parallel part: iterations 0 to (LEN_1D-1)/2 have no loop-carried dependencies
        #pragma omp parallel for private(x) 
        for (int i = 0; i <= (LEN_1D-1)/2; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        // Sequential part: iterations (LEN_1D-1)/2+1 to LEN_1D-1 depend on earlier iterations
        for (int i = (LEN_1D-1)/2+1; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
