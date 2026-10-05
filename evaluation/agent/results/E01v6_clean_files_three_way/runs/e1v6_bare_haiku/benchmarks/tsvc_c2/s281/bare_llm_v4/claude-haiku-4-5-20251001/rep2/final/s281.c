#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: iterations 0 to LEN_1D/2-1
        // Each iteration i writes a[i] (lower half) and reads a[LEN_1D-1-i] (upper half, unmodified).
        // No cross-iteration dependencies within this phase.
        #pragma omp parallel for private(x)
        for (int i = 0; i < LEN_1D/2; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        // Phase 2: iterations LEN_1D/2 to LEN_1D-1
        // Each iteration i writes a[i] (upper half) and reads a[LEN_1D-1-i] (lower half, computed in phase 1).
        // No cross-iteration dependencies within this phase; phase 1 must complete before phase 2 starts (implicit barrier).
        #pragma omp parallel for private(x)
        for (int i = LEN_1D/2; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
