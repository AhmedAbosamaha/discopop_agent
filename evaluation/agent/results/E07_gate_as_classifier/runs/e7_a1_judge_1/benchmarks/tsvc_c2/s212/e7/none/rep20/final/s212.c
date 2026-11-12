#include "data.h"

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Update b using current a values before modifying a
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] += a[i + 1] * d[i];
        }

        // Then update a
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
