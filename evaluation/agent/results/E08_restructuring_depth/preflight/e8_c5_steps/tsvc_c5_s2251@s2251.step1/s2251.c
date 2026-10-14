#include <stdlib.h>
#include "data.h"

real_t kernel_s2251(void)
{
    real_t *tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(tmp) 
        for (int i = 0; i < LEN_1D; i++) {
            tmp[i] = b[i]+c[i];
        }
        real_t s = (real_t)0.0;
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s*e[i];
            s = tmp[i];
            b[i] = a[i]+d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
