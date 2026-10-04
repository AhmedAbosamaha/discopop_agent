#include "data.h"

real_t kernel_vpvtv(void)
{
    #pragma omp parallel for 
    for (int i = 0; i < LEN_1D; i++) {
        a[i] += b[i] * c[i];
    }
    return (real_t)0;
}
