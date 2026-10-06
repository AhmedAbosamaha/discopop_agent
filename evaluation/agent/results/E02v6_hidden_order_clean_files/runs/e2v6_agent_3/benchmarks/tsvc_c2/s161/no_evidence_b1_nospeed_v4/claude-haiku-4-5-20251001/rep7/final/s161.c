#include "data.h"
#include <stdlib.h>

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *c_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(c_temp) 
        for (int j = 0; j < LEN_1D; ++j) {
            c_temp[j] = c[j];
        }

        #pragma omp parallel for shared(c_temp) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c_temp[i+1] = a[i] + d[i] * d[i];
            }
        }

        #pragma omp parallel for shared(c_temp) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] >= (real_t)0.) {
                a[i] = c_temp[i] + d[i] * e[i];
            }
        }

        #pragma omp parallel for shared(c_temp) 
        for (int j = 0; j < LEN_1D; ++j) {
            c[j] = c_temp[j];
        }
        free(c_temp);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
