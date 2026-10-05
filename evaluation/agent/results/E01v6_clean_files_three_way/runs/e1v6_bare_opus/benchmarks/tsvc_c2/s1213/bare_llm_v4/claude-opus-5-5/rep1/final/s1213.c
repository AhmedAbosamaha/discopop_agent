#include "data.h"

real_t kernel_s1213(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: b[i] uses a[i+1] before it is overwritten (old a). */
        #pragma omp parallel for default(none) shared(a, b, d) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }
        /* Pass 2: a[i] uses b[i-1] just produced (b[0] unchanged). */
        #pragma omp parallel for default(none) shared(a, b, c) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
