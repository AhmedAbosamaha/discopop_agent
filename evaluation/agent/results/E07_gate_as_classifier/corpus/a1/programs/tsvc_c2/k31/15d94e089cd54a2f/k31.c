#include "data.h"
#include <stdlib.h>

real_t kernel_k31(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            real_t v_val = v[i + off];
            real_t u_val = u[i + far];
            u[i] += v_val * c[i];
            v[i] = u_val * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
