#include <stdlib.h>
#include "data.h"

real_t kernel_s243(void)
{
    static real_t *tmp;
    if (!tmp) tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D; i++) tmp[i] = a[i];
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D-1; i++) {
        a[i] = b[i] + c[i  ] * d[i];
        b[i] = a[i] + d[i  ] * e[i];
        a[i] = b[i] + tmp[i+1] * d[i];
    }
    return (real_t)0;
}
