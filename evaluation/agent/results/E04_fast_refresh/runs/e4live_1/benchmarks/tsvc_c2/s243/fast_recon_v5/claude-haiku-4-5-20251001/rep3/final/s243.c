#include <stdlib.h>
#include "data.h"

real_t kernel_s243(void)
{
    real_t *a_new = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));
    real_t *b_new = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_new,b_new) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a_new[i] = b[i] + c[i  ] * d[i];
            b_new[i] = a_new[i] + d[i  ] * e[i];
            a_new[i] = b_new[i] + a[i+1] * d[i];
        }
        #pragma omp parallel for shared(a_new,b_new) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_new[i];
            b[i] = b_new[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_new);
    free(b_new);
    return (real_t)0;
}
