#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        int mid = (LEN_1D - 1) / 2;

        // Stage 1: Iterations 0 to mid (no loop-carried dependencies)
        // These iterations read from the upper half of a, which is not written in this stage
        #pragma omp parallel for firstprivate(mid) private(x) 
        for (int i = 0; i <= mid; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        // Stage 2: Iterations mid+1 to LEN_1D-1 (no loop-carried dependencies within this stage)
        // These iterations read from the lower half of a, which was written in Stage 1
        #pragma omp parallel for firstprivate(mid) private(x) 
        for (int i = mid + 1; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
