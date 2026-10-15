#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s2251(void)
{
    real_t* s_array = (real_t*)malloc((LEN_1D + 1) * sizeof(real_t));
    real_t* b_old = (real_t*)malloc(LEN_1D * sizeof(real_t));
    memcpy(b_old, b, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Precompute s values from saved b array
        s_array[0] = (real_t)0.0;
        #pragma omp parallel for shared(b_old,s_array) 
        for (int i = 0; i < LEN_1D; i++) {
            s_array[i+1] = b_old[i] + c[i];
        }

        // Compute a and b using precomputed s values
        #pragma omp parallel for shared(s_array) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_array[i]*e[i];
            b[i] = a[i]+d[i];
        }

        dummy(a, b, c, d, e);
        memcpy(b_old, b, LEN_1D * sizeof(real_t));
    }

    free(s_array);
    free(b_old);
    return (real_t)0;
}
