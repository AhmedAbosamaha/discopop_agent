#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    real_t *s_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // First pass: compute all products s[i] = b[i] * c[i] in parallel
        // Each iteration writes to s_temp[i] independently, only reads b[i] and c[i]
        #pragma omp parallel for schedule(static) private(i)
        for (int i = 0; i < LEN_1D; i++) {
            s_temp[i] = b[i] * c[i];
        }

        // Second pass: compute a[i] = s[i] + s[i-1] in parallel
        // a[0] = s[0] + 0 (initial t value)
        // a[i] = s[i] + s[i-1] for i > 0
        // Each iteration reads s_temp[i] and s_temp[i-1], writes to a[i] only
        #pragma omp parallel for schedule(static) private(i)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_temp[i] + (i > 0 ? s_temp[i-1] : (real_t)0.);
        }

        dummy(a, b, c, d, e);
    }

    free(s_temp);
    return (real_t)0;
}
