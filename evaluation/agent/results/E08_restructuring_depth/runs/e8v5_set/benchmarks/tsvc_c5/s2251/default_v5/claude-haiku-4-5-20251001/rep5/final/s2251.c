#include <stdlib.h>
#include "data.h"

real_t kernel_s2251(void)
{
    real_t *s_array = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // First pass: compute s values sequentially (s[i] depends on b[i-1], c[i-1])
        s_array[0] = (real_t)0.0;
        #pragma omp parallel for shared(s_array) 
        for (int i = 1; i < LEN_1D; i++) {
            s_array[i] = b[i-1]+c[i-1];
        }

        // Second pass: compute a and b using precomputed s_array (now parallel)
        #pragma omp parallel for shared(s_array) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_array[i]*e[i];
            b[i] = a[i]+d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(s_array);
    return (real_t)0;
}
