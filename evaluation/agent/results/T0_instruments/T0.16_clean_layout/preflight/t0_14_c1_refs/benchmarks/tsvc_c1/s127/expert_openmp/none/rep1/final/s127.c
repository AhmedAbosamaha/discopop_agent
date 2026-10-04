#include "data.h"

real_t kernel_s127(void)
{
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D/2; i++) {
        a[2*i] = b[i] + c[i] * d[i];
        a[2*i+1] = b[i] + d[i] * e[i];
    }
    return (real_t)0;
}
