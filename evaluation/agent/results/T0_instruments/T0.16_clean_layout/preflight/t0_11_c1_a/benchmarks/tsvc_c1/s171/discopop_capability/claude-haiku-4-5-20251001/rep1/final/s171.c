#include "data.h"

real_t kernel_s171(void)
{
    #pragma omp parallel for 
    for (int i = 0; i < LEN_1D; i++) {
        a[i * inc] += b[i];
    }
    return (real_t)0;
}
