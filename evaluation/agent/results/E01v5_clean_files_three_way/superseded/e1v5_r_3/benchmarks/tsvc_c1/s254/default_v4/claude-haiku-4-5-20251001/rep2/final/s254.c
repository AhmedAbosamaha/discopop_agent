#include "data.h"

real_t kernel_s254(void)
{
    a[0] = (b[0] + b[LEN_1D-1]) * (real_t).5;
    #pragma omp parallel for 
    for (int i = 1; i < LEN_1D; i++) {
        a[i] = (b[i] + b[i-1]) * (real_t).5;
    }
    return (real_t)0;
}
