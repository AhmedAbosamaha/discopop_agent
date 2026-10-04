#include "data.h"

real_t kernel_k23(void)
{
    for (long i = 1; i < LEN_1D; i++) {
        u[i] += w[i] * c[i];
        v[i] = x[i] * d[i] + c[i];
    }
    return (real_t)0;
}
