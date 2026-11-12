#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* a_new = (real_t*)malloc((LEN_1D-1) * sizeof(real_t));
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
            a_new[i] = b[i] + a[i+1] * d[i];
        }
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i+1] = a_new[i];
        }
        dummy(a, b, c, d, e);
        free(a_new);
    }
    return (real_t)0;
}
