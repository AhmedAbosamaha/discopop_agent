#include "data.h"
#include <stdlib.h>

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *a_init = (real_t *)malloc(LEN_1D * sizeof(real_t));
        for (int i = 0; i < LEN_1D; ++i) {
            a_init[i] = a[i];
        }
        #pragma omp parallel for shared(a_init) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a_init[i] + d[i] * d[i];
            }
        }
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] >= (real_t)0.) {
                a[i] = c[i] + d[i] * e[i];
            }
        }
        free(a_init);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
