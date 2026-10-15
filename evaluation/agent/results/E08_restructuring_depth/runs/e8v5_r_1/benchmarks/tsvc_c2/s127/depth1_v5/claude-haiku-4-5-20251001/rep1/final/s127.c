#include <stdlib.h>
#include "data.h"

real_t kernel_s127(void)
{
    real_t *d_copy = (real_t *)malloc((LEN_1D/2) * sizeof(real_t));
    real_t *e_copy = (real_t *)malloc((LEN_1D/2) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Copy d and e to break loop-carried dependence:
        // each iteration uses a snapshot of these arrays,
        // independent of prior dummy() calls
        #pragma omp parallel for shared(d_copy,e_copy) 
        for (int j = 0; j < LEN_1D/2; j++) {
            d_copy[j] = d[j];
            e_copy[j] = e[j];
        }

        #pragma omp parallel for shared(d_copy,e_copy) 
        for (int i = 0; i < LEN_1D/2; i++) {
            a[2*i] = b[i] + c[i] * d_copy[i];
            a[2*i+1] = b[i] + d_copy[i] * e_copy[i];
        }
        dummy(a, b, c, d, e);
    }

    free(d_copy);
    free(e_copy);
    return (real_t)0;
}
