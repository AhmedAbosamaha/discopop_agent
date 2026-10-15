#include <stdlib.h>
#include "data.h"

real_t kernel_s2251(void)
{
    // Allocate outside the repeated loop to avoid per-iteration overhead
    real_t* s_vals = (real_t*)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Precompute s values to eliminate loop-carried scalar dependency
        s_vals[0] = (real_t)0.0;
        #pragma omp parallel for shared(s_vals) 
        for (int i = 1; i < LEN_1D; i++) {
            s_vals[i] = b[i-1] + c[i-1];
        }

        // Main loop: no loop-carried dependencies after precomputation
        #pragma omp parallel for shared(s_vals) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_vals[i]*e[i];
            b[i] = a[i]+d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(s_vals);
    return (real_t)0;
}
