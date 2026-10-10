#include "data.h"
#include <stdlib.h>

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *a_new = (real_t *)malloc(LEN_1D * sizeof(real_t));

        #pragma omp parallel for shared(a_new) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            a_new[i] = a[i];
        }

        #pragma omp parallel for shared(a_new) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = a_new[i] + d[i] * d[i];
            }
        }

        #pragma omp parallel for shared(a_new) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (!(b[i] < (real_t)0.)) {
                a_new[i] = c[i] + d[i] * e[i];
            }
        }

        #pragma omp parallel for shared(a_new) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = a_new[i];
        }

        free(a_new);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
