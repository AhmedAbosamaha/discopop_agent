#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    real_t t;
    real_t *s = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Pass 1: Compute s values (parallel candidate: no loop-carried dependence)
        #pragma omp parallel for shared(s) 
        for (int i = 0; i < LEN_1D; i++) {
            s[i] = b[i] * c[i];
        }

        // Pass 2: Compute a values with cumulative sum (sequential, dependence moved out)
        t = (real_t) 0.;
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s[i] + t;
            t = s[i];
        }

        dummy(a, b, c, d, e);
    }

    free(s);
    return (real_t)0;
}
