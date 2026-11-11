#include "data.h"
#include <stdlib.h>

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: compute a[] using b[] (b[] is only read, not written yet)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[i-1] + c[i] * d[i];
        }

        // Phase 2: compute b[] using a[] (no loop-carry on b[])
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = a[i] + c[i] * e[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
