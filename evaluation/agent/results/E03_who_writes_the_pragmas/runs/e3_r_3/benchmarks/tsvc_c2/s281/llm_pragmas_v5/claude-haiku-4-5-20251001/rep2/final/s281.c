#include <stdlib.h>
#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        int half = LEN_1D / 2;

        // Phase 1: iterations 0 to half-1 write first half of a[].
        // Each iteration i writes a[i]; these are independent.
        #pragma omp parallel for private(x)
        for (int i = 0; i < half; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        // Phase 2: iterations half to LEN_1D-1 read from a[] that phase 1 wrote.
        // Iteration j reads a[LEN_1D-j-1], which phase 1 iteration (LEN_1D-j-1) wrote.
        // Each iteration is independent (different write indices from phase 1).
        #pragma omp parallel for private(x)
        for (int i = half; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
