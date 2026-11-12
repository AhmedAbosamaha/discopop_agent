#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: first half of iterations (i < (LEN_1D+1)/2)
        // These write to the first half of array a while reading from the second half
        // No cross-iteration dependencies within this phase
        #pragma omp parallel for private(x) 
        for (int i = 0; i < (LEN_1D + 1) / 2; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        // Phase 2: second half of iterations (i >= (LEN_1D+1)/2)
        // These read from values written by phase 1, write to the second half
        // No cross-iteration dependencies within this phase
        for (int i = (LEN_1D + 1) / 2; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
