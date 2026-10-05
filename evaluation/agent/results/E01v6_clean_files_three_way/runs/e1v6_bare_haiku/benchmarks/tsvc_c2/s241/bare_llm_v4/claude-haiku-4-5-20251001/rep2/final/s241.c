#include "data.h"

real_t kernel_s241(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // First loop: compute a[i] values (independent iterations)
        #pragma omp parallel for schedule(static) shared(a, b, c, d) private(i)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
        }
        // Second loop: compute b[i] values (independent iterations after a[] is complete)
        #pragma omp parallel for schedule(static) shared(a, b, d) private(i)
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = a[i] * a[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
