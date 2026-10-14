#include <stdlib.h>
#include "data.h"

real_t kernel_s2251(void)
{
    real_t *b_new = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            real_t s;
            if (i == 0) {
                s = (real_t)0.0;
            } else {
                s = b[i-1]+c[i-1];
            }
            a[i] = s*e[i];
        }
        #pragma omp parallel for shared(b_new) 
        for (int i = 0; i < LEN_1D; i++) {
            b_new[i] = a[i]+d[i];
        }
        dummy(a, b_new, c, d, e);
        #pragma omp parallel for shared(b_new) 
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = b_new[i];
        }
    }

    free(b_new);
    return (real_t)0;
}
