#include <stdlib.h>
#include "data.h"

real_t kernel_s211(void)
{
    static real_t *tmp;
    if (!tmp) tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D; i++) tmp[i] = b[i];
    #pragma omp parallel for
    for (int i = 1; i < LEN_1D-1; i++) b[i] = tmp[i + 1] - e[i] * d[i];
    #pragma omp parallel for
    for (int i = 1; i < LEN_1D-1; i++) a[i] = b[i - 1] + c[i] * d[i];
    return (real_t)0;
}
