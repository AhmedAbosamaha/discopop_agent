#include "data.h"

real_t kernel_s244(void)
{
    real_t a_last_saved = a[LEN_1D-1];
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
            if (i == LEN_1D-2) {
                a[LEN_1D-1] = b[i] + a_last_saved * d[i];
            } else {
                a[i+1] = b[i] + a[i+1] * d[i];
            }
        }
        a_last_saved = a[LEN_1D-1];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
