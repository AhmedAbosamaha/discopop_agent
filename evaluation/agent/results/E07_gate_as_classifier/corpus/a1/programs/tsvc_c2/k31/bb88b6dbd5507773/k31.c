#include "data.h"

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = LEN_1D - 1; i > 1; i--) {
            u[i] += v[i + off] * c[i];
            v[i] = u[i + far] * d[i] + c[i];
        }
        u[1] += v[1 + off] * c[1];
        v[1] = u[1 + far] * d[1] + c[1];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
