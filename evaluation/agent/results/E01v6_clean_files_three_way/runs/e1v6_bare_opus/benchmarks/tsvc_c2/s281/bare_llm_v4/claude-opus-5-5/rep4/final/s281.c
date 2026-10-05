#include "data.h"

real_t kernel_s281(void)
{
    int half = (LEN_1D + 1) / 2;
    for (int nl = 0; nl < iterations; nl++) {
        /* first half: a[LEN_1D-i-1] still holds its original value
           (or is the element this same iteration writes after reading) */
        #pragma omp parallel for shared(a, b, c, half) schedule(static)
        for (int i = 0; i < half; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        /* second half: reads a[LEN_1D-i-1] < half, written by the loop above */
        #pragma omp parallel for shared(a, b, c, half) schedule(static)
        for (int i = half; i < LEN_1D; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
