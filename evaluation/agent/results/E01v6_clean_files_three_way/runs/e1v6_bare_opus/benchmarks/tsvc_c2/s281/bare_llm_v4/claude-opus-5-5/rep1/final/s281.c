#include "data.h"

real_t kernel_s281(void)
{
    const int h = (LEN_1D + 1) / 2;
    for (int nl = 0; nl < iterations; nl++) {
        /* first half: reads a[LEN_1D-i-1] with index >= i, still original */
        #pragma omp parallel for schedule(static) default(none) shared(a, b, c) firstprivate(h)
        for (int i = 0; i < h; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        /* second half: reads a[LEN_1D-i-1] (< h), written by first loop */
        #pragma omp parallel for schedule(static) default(none) shared(a, b, c) firstprivate(h)
        for (int i = h; i < LEN_1D; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
