#include "data.h"

real_t kernel_s293(void)
{
    real_t a0 = a[0];
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D; i++) a[i] = a0;
    return (real_t)0;
}
