#include "data.h"
#include <string.h>
#include <stdlib.h>

real_t kernel_s211(void)
{
    real_t *b_orig = malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(b_orig, b, sizeof(real_t) * LEN_1D);

        #pragma omp parallel for shared(b_orig) 
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = b_orig[i + 1] - e[i] * d[i];
        }
        #pragma omp parallel for 
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i - 1] + c[i] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(b_orig);
    return (real_t)0;
}
