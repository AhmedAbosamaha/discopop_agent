#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Snapshot b[] at the start of this iteration
        real_t *b_prev = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (int i = 0; i < LEN_1D; i++) {
            b_prev[i] = b[i];
        }

        // Phase 1: compute a[] using b_prev (no loop-carry)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b_prev[i-1] + c[i] * d[i];
        }

        // Phase 2: compute b[] using a[] (no loop-carry)
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = a[i] + c[i] * e[i];
        }

        free(b_prev);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
