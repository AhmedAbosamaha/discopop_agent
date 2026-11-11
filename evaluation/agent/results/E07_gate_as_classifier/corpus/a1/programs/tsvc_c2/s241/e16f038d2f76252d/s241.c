#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s241(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *a_copy = malloc(LEN_1D * sizeof(real_t));
        memcpy(a_copy, a, LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(a_copy) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * a_copy[i+1] * d[i];
        }
        free(a_copy);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
