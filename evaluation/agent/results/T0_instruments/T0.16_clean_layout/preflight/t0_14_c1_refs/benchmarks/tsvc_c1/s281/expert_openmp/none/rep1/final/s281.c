#include "data.h"

real_t kernel_s281(void)
{
    int half = (LEN_1D + 1) / 2;
    #pragma omp parallel for
    for (int i = 0; i < half; i++) {
        real_t x = a[LEN_1D-i-1] + b[i] * c[i];
        a[i] = x-(real_t)1.0;
        b[i] = x;
    }
    #pragma omp parallel for
    for (int i = half; i < LEN_1D; i++) {
        real_t x = a[LEN_1D-i-1] + b[i] * c[i];
        a[i] = x-(real_t)1.0;
        b[i] = x;
    }
    return (real_t)0;
}
