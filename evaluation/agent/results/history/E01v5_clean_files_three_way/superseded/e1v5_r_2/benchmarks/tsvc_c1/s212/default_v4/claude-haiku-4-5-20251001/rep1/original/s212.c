#include "data.h"

real_t kernel_s212(void)
{
    for (int i = 0; i < LEN_1D-1; i++) {
        a[i] *= c[i];
        b[i] += a[i + 1] * d[i];
    }
    return (real_t)0;
}
