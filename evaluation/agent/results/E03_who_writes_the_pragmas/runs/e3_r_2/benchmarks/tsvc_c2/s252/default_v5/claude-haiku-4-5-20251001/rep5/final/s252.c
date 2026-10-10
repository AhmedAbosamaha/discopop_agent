#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    real_t t;
    real_t *s = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute products (parallelizable, no loop-carries)
        #pragma omp parallel for shared(s) 
        for (int i = 0; i < LEN_1D; i++) {
            s[i] = b[i] * c[i];
        }
        // Phase 2: Compute cumulative sum (sequential)
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
