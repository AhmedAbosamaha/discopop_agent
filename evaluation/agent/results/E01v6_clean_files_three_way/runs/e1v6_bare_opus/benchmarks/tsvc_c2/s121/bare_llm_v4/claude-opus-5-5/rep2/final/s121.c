#include <stdlib.h>
#include "data.h"

real_t kernel_s121(void)
{
    real_t *tmp = (real_t *)malloc(sizeof(real_t) * (LEN_1D > 1 ? LEN_1D - 1 : 1));
    for (int nl = 0; nl < iterations; nl++) {
        /* snapshot old a[i+1] values (anti-dependence removed) */
        #pragma omp parallel for default(none) shared(a, tmp) schedule(static)
        for (int i = 0; i < LEN_1D - 1; i++) {
            tmp[i] = a[i + 1];
        }
        #pragma omp parallel for default(none) shared(a, b, tmp) schedule(static)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i] = tmp[i] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
