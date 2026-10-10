#include "data.h"

real_t kernel_s281(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Process first half of iterations (read from upper indices)
        // Each iteration reads a[LEN_1D-1-i] where the index is in the upper half,
        // not yet written in this loop, so no intra-phase dependence.
        #pragma omp parallel for shared(a, b, c)
        for (int i = 0; i < (LEN_1D + 1) / 2; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        // Phase 2: Process second half of iterations (read from lower indices)
        // Each iteration reads a[LEN_1D-1-i] where the index was written in phase 1.
        // No iteration in this phase reads what another in this phase writes.
        #pragma omp parallel for shared(a, b, c)
        for (int i = (LEN_1D + 1) / 2; i < LEN_1D; i++) {
            real_t x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
