#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    real_t *a_new = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));

    // Compute initial a_new before main loop
    #pragma omp parallel for shared(a_new) 
    for (int i = 0; i < LEN_1D-1; i++) {
        a_new[i] = a[i + 1] + b[i];
    }

    for (int nl = 0; nl < iterations; nl++) {
        // Apply computed a_new
        #pragma omp parallel for shared(a_new) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_new[i];
        }
        dummy(a, b, c, d, e);
        // Compute a_new for next iteration
        if (nl + 1 < iterations) {
            #pragma omp parallel for shared(a_new) 
            for (int i = 0; i < LEN_1D-1; i++) {
                a_new[i] = a[i + 1] + b[i];
            }
        }
    }

    free(a_new);
    return (real_t)0;
}
