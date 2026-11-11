#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s243(void)
{
    real_t *a_prev = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(a_prev, a, LEN_1D * sizeof(real_t));

        #pragma omp parallel for shared(a_prev) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_prev[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_prev);
    return (real_t)0;
}
