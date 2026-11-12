#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    real_t *s_array = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Compute s values: s_array[i] = b[i] * c[i] (parallel loop, no dependencies)
        #pragma omp parallel for shared(s_array) 
        for (int i = 0; i < LEN_1D; i++) {
            s_array[i] = b[i] * c[i];
        }

        // Compute a values using shift pattern: a[i] = s_array[i] + prev
        // where prev carries the previous s value, matching original accumulation
        real_t prev = (real_t) 0.;
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_array[i] + prev;
            prev = s_array[i];
        }

        dummy(a, b, c, d, e);
    }

    free(s_array);
    return (real_t)0;
}
