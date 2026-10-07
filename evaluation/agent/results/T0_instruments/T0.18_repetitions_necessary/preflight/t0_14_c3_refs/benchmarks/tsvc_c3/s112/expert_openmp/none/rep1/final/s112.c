#include <stdlib.h>
#include "data.h"

real_t kernel_s112(void)
{
    real_t *tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for
        for (int i = 0; i < LEN_1D; i++) tmp[i] = a[i];
        #pragma omp parallel for
        for (int i = LEN_1D - 2; i >= 0; i--) a[i+1] = tmp[i] + b[i];
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
