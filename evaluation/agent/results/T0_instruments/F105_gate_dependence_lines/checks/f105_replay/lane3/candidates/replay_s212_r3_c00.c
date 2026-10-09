#include "data.h"

real_t kernel_s212(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Save a[i+1] values before modifying a[i]
        real_t a_next[LEN_1D-1];
        for (int i = 0; i < LEN_1D-1; i++) {
            a_next[i] = a[i+1];
        }

        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] *= c[i];
            b[i] += a_next[i] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
