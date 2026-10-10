#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        // Parallelize both halves within a single parallel region to amortize overhead
        #pragma omp parallel
        {
            // First half: iterations 0 to LEN_1D/2-1 (no loop-carried dependences)
            #pragma omp for private(x)
            for (int i = 0; i < LEN_1D/2; i++) {
                x = a[LEN_1D-i-1] + b[i] * c[i];
                a[i] = x-(real_t)1.0;
                b[i] = x;
            }
            // Implicit barrier here; all threads sync before second half

            // Second half: iterations LEN_1D/2 to LEN_1D-1 (depends on first half, no inter-iteration dependence)
            #pragma omp for private(x)
            for (int i = LEN_1D/2; i < LEN_1D; i++) {
                x = a[LEN_1D-i-1] + b[i] * c[i];
                a[i] = x-(real_t)1.0;
                b[i] = x;
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
