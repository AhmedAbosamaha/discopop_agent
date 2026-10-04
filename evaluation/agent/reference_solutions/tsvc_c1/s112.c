#include <stdlib.h>
#include "data.h"

real_t kernel_s112(void)
{
    static real_t *tmp;
    if (!tmp) tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D; i++) tmp[i] = a[i];
    #pragma omp parallel for
    for (int i = LEN_1D - 2; i >= 0; i--) a[i+1] = tmp[i] + b[i];
    return (real_t)0;
}
