#include <stdlib.h>
#include "data.h"

real_t kernel_s2251(void)
{
    real_t *s_vals = malloc((LEN_1D + 1) * sizeof(real_t));
    s_vals[0] = (real_t)0.0;

    #pragma omp parallel for shared(s_vals) 
    for (int i = 0; i < LEN_1D; i++) {
        s_vals[i+1] = b[i]+c[i];
    }

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(s_vals) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_vals[i]*e[i];
            b[i] = a[i]+d[i];
        }
        dummy(a, b, c, d, e);
        if (nl < iterations - 1) {
            #pragma omp parallel for shared(s_vals) 
            for (int i = 0; i < LEN_1D; i++) {
                s_vals[i+1] = b[i]+c[i];
            }
        }
    }
    free(s_vals);
    return (real_t)0;
}
