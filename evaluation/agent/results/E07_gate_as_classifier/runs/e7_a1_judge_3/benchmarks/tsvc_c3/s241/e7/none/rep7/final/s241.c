#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s241(void)
{
    real_t *a_old = malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(a_old, a, sizeof(real_t) * LEN_1D);
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
        }
        #pragma omp parallel for shared(a_old) 
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = a[i] * a_old[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
