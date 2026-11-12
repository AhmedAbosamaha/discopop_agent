#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    real_t *s_temp = (real_t*) malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute s_temp[i] = b[i] * c[i] (independent across i)
        #pragma omp parallel for shared(s_temp) 
        for (int i = 0; i < LEN_1D; i++) {
            s_temp[i] = b[i] * c[i];
        }
        // Phase 2: Compute a[i] using the sliding window (unavoidable sequential dependence)
        a[0] = s_temp[0];
        #pragma omp parallel for shared(s_temp) 
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = s_temp[i] + s_temp[i-1];
        }
        dummy(a, b, c, d, e);
    }
    free(s_temp);
    return (real_t)0;
}
