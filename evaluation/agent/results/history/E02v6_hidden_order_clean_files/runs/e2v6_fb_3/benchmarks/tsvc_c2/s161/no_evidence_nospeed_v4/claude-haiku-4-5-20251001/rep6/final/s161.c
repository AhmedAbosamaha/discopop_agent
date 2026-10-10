#include "data.h"
#include <stdlib.h>

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* c_updates = (real_t*) malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(c_updates) 
        for (int i = 0; i < LEN_1D; i++) c_updates[i] = c[i];

        // Pass 1: Compute c[i+1] updates where b[i] < 0, using a[i] from previous outer iteration
        #pragma omp parallel for firstprivate(c_updates) 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c_updates[i+1] = a[i] + d[i] * d[i];
            }
        }

        // Apply c updates
        #pragma omp parallel for shared(c_updates) 
        for (int i = 0; i < LEN_1D; i++) c[i] = c_updates[i];

        // Pass 2: Compute a[i] where b[i] >= 0, using updated c[i]
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] >= (real_t)0.) {
                a[i] = c[i] + d[i] * e[i];
            }
        }

        free(c_updates);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
