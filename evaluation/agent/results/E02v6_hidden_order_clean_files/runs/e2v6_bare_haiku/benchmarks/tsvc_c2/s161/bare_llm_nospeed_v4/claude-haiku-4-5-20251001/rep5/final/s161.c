#include "data.h"

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: write to c when b[i] < 0
        // Each iteration i writes to c[i+1], so different iterations write to different indices.
        #pragma omp parallel for shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a[i] + d[i] * d[i];
            }
        }
        // Phase 2: write to a when b[i] >= 0
        // Each iteration i reads c[i] (written in phase 1 iteration i-1 if applicable)
        // and writes to a[i]. Different iterations write to different indices, no race.
        #pragma omp parallel for shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] >= (real_t)0.) {
                a[i] = c[i] + d[i] * e[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
