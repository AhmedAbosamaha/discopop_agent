#include "data.h"

real_t kernel_k31(void)
{
    for (long i = 1; i < LEN_1D; i++) {
        u[i] += v[i + off] * c[i];
        v[i] = u[i + far] * d[i] + c[i];
    }
    return (real_t)0;
}
