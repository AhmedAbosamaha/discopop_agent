#include "data.h"

real_t kernel_s254(void)
{
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D; i++) {
        real_t x = (i > 0) ? b[i-1] : b[LEN_1D-1];
        a[i] = (b[i] + x) * (real_t).5;
    }
    return (real_t)0;
}
