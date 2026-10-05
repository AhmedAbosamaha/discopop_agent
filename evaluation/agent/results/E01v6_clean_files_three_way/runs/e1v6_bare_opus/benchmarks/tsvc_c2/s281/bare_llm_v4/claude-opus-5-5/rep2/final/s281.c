#include "data.h"

real_t kernel_s281(void)
{
    const int half = (LEN_1D + 1) / 2;
    for (int nl = 0; nl < iterations; nl++) {
        /* First half: a[LEN_1D-i-1] is still the old value (index >= i). */
        #pragma omp parallel for default(none) shared(a, b, c) firstprivate(half) schedule(static)
        for (int i = 0; i < half; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        /* Second half: a[LEN_1D-i-1] (index < half) was updated above. */
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
