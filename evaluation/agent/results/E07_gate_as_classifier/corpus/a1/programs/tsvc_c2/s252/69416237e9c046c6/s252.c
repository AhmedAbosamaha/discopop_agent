#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    real_t t, s;
    for (int nl = 0; nl < iterations; nl++) {
        // Allocate buffer for intermediate products
        real_t* s_vals = (real_t*)malloc(LEN_1D * sizeof(real_t));

        // First pass: compute all products (Do-All, parallelizable)
        #pragma omp parallel for shared(s_vals) 
        for (int i = 0; i < LEN_1D; i++) {
            s_vals[i] = b[i] * c[i];
        }

        // Second pass: compute results using precomputed products
        t = (real_t) 0.;
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_vals[i] + t;
            t = s_vals[i];
        }

        free(s_vals);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
