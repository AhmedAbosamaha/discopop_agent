#include <stdlib.h>
#include "data.h"

real_t kernel_s121(void)
{
    static real_t *tmp;
    if (!tmp) tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D; i++) tmp[i] = a[i];
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D-1; i++) a[i] = tmp[i + 1] + b[i];
    return (real_t)0;
}
