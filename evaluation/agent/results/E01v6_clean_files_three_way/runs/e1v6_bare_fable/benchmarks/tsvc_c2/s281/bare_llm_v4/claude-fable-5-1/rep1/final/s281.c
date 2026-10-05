#include "data.h"

real_t kernel_s281(void)
{
    const int half = LEN_1D / 2;
    for (int nl = 0; nl < iterations; nl++) {
        /* Lower half: reads a[LEN_1D-i-1] from the (still untouched) upper half. */
#pragma omp parallel for default(none) shared(a, b, c) firstprivate(half) schedule(static)
        for (int i = 0; i < half; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        /* Upper half: reads a[LEN_1D-i-1] from the lower half, now final. */
#pragma omp parallel for default(none) shared(a, b, c) firstprivate(half) schedule(static)
        for (int i = half; i < LEN_1D; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
