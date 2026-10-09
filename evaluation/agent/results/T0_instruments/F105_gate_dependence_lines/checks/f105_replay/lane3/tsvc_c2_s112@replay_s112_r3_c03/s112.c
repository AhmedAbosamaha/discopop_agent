#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s112(void)
{
    real_t *a_orig = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(a_orig, a, (LEN_1D - 1) * sizeof(real_t));

        #pragma omp parallel for shared(a_orig) 
        for (int i = LEN_1D - 2; i >= 0; i--) {
            a[i+1] = a_orig[i] + b[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_orig);
    return (real_t)0;
}
