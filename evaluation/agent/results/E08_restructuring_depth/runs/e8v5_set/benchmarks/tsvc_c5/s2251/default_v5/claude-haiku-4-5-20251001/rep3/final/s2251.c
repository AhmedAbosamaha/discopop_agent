#include "data.h"
#include <stdlib.h>

real_t kernel_s2251(void)
{
    real_t *s_values = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Precompute s values in sequence to extract the dependence
        real_t s_temp = (real_t)0.0;
        for (int i = 0; i < LEN_1D; i++) {
            s_values[i] = s_temp;
            s_temp = b[i] + c[i];
        }

        // Compute a and b without loop-carried dependence on s
        #pragma omp parallel for shared(s_values) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_values[i]*e[i];
            b[i] = a[i]+d[i];
        }

        dummy(a, b, c, d, e);
    }

    free(s_values);
    return (real_t)0;
}
