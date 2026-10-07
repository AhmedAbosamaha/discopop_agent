#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *c_temp = malloc(LEN_1D * sizeof(real_t));
        memcpy(c_temp, c, LEN_1D * sizeof(real_t));

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

        memcpy(c, c_temp, LEN_1D * sizeof(real_t));
        free(c_temp);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
