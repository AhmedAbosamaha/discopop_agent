#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    /* Iteration i reads a[LEN_1D-1-i]; that element was already rewritten
       iff LEN_1D-1-i < i.  So i < half reads original values (disjoint from
       other first-half writes), i >= half reads values the first half wrote. */
    const int half = (LEN_1D + 1) / 2;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for private(x) schedule(static)
        for (int i = 0; i < half; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        #pragma omp parallel for private(x) schedule(static)
        for (int i = half; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
