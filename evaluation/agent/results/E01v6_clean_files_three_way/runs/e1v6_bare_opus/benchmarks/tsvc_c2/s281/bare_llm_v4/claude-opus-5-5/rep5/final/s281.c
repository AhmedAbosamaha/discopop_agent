#include "data.h"

real_t kernel_s281(void)
{
    /* Iterations i < half read a[LEN_1D-i-1] before it is overwritten
       (original values); iterations i >= half read a[LEN_1D-i-1] that was
       written by iteration LEN_1D-i-1 < half.  Splitting at half makes
       each phase independent; the implicit barrier carries the dependence. */
    const int half = (LEN_1D + 1) / 2;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for schedule(static) shared(a, b, c)
        for (int i = 0; i < half; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        #pragma omp parallel for schedule(static) shared(a, b, c)
        for (int i = half; i < LEN_1D; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
