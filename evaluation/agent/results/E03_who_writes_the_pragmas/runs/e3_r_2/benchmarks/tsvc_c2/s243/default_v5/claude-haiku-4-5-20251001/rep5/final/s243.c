#include "data.h"
#include <stdlib.h>

real_t kernel_s243(void)
{
    // Allocate buffer once outside the nl-loop to avoid repeated malloc/free
    real_t* a_old = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Save old values of a before transformation
        #pragma omp parallel for shared(a_old) 
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

        // Phase 1: Compute new a[i] and b[i] (forward loop, parallelizable)
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
        }

        // Phase 2: Compute final a[i] using saved old values (reversed loop, parallelizable)
        #pragma omp parallel for shared(a_old) 
        for (int i = LEN_1D-2; i >= 0; i--) {
            a[i] = b[i] + a_old[i+1] * d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
