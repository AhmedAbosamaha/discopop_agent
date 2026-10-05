#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        int mid = (LEN_1D + 1) / 2;
        #pragma omp parallel for firstprivate(mid) private(x) 
        for (int i = 0; i < mid; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        for (int i = mid; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
