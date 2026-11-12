#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t b_snapshot[LEN_1D];
        for (int i = 0; i < LEN_1D; i++) {
            b_snapshot[i] = b[i];
        }

        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b_snapshot[i-1] + c[i] * d[i];
            b[i] = a[i] + c[i] * e[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
