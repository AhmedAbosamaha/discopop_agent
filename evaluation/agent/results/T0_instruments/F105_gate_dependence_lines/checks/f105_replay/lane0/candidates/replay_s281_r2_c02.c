#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        int half = LEN_1D / 2;

        // Phase 1: iterations 0 to half-1 (no loop-carried dependence on a within phase)
        for (int i = 0; i < half; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        // Phase 2: iterations half to LEN_1D-1 (no loop-carried dependence on a within phase)
        // These iterations read values written by phase 1
        for (int i = half; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            a[i] = x-(real_t)1.0;
            b[i] = x;
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
