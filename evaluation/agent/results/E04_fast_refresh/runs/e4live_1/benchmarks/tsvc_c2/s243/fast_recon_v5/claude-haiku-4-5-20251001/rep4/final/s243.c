#include "data.h"
#include <stdlib.h>

real_t kernel_s243(void)
{
    real_t *temp_a = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *temp_b = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(temp_b,temp_a) 
        for (int i = 0; i < LEN_1D-1; i++) {
            real_t a_temp = b[i] + c[i  ] * d[i];
            real_t b_temp = a_temp + d[i  ] * e[i];
            temp_a[i] = b_temp + a[i+1] * d[i];
            temp_b[i] = b_temp;
        }
        #pragma omp parallel for shared(temp_b,temp_a) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = temp_a[i];
            b[i] = temp_b[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp_a);
    free(temp_b);
    return (real_t)0;
}
