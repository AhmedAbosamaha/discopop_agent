#include "data.h"

real_t kernel_s000(void)
{
    int i;
    #pragma omp parallel for 
    for (i = 0; i < LEN_1D; i++) {
        a[i] = b[i] + 1;
    }
    return (real_t)0;
}
