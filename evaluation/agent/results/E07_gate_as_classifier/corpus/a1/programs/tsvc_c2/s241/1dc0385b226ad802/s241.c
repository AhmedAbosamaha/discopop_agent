#include "data.h"

real_t kernel_s241(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Process even indices: no inter-iteration dependence (each reads a[odd])
        for (int i = 0; i < LEN_1D-1; i += 2) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * a[i+1] * d[i];
        }

        // Process odd indices: reads a[even] already computed in first pass
        for (int i = 1; i < LEN_1D-1; i += 2) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * a[i+1] * d[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
