#include <stdlib.h>
#include "data.h"

real_t kernel_s241(void)
{
    real_t *tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) tmp[i] = a[i];
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * tmp[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
