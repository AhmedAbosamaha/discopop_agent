#include <stdlib.h>
#include "data.h"

real_t kernel_s241(void)
{
    real_t *tmp = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        /* pass 1: new a[i] into tmp, b[i] uses old a[i+1] (a untouched) */
        #pragma omp parallel for default(none) shared(a, b, c, d, tmp) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            real_t t = b[i] * c[i] * d[i];
            tmp[i] = t;
            b[i] = t * a[i+1] * d[i];
        }
        /* pass 2: commit new a */
        #pragma omp parallel for default(none) shared(a, tmp) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = tmp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
