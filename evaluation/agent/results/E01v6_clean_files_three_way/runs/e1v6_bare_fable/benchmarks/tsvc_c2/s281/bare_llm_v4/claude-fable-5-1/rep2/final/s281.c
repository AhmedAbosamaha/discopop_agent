#include "data.h"

real_t kernel_s281(void)
{
    /* Iterations with i <= LEN_1D-1-i read a[] values untouched in this
     * sweep; the remaining ones read a[LEN_1D-1-i] produced by the first
     * group.  Split at half so each group is independent. */
    const int half = (LEN_1D + 1) / 2;
    for (int nl = 0; nl < iterations; nl++) {
#pragma omp parallel for default(none) shared(a, b, c) firstprivate(half) schedule(static)
        for (int i = 0; i < half; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
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
