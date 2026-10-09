#include "data.h"
#include <stdlib.h>

real_t kernel_s243(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *a_old = (real_t *)malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(a_old) 
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }
        #pragma omp parallel for shared(a_old) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_old[i+1] * d[i];
        }
        free(a_old);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
