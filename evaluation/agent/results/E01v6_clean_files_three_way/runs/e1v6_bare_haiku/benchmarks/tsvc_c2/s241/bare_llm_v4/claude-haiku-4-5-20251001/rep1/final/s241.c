#include "data.h"
#include <string.h>

real_t kernel_s241(void)
{
    real_t *a_orig = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Save current state of a before parallel loop to break loop-carried dependence
        memcpy(a_orig, a, LEN_1D * sizeof(real_t));

        // Parallel loop: each iteration reads a[i+1] from saved state and writes to a[i], b[i]
        #pragma omp parallel for shared(a, b, c, d, a_orig)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * a_orig[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_orig);
    return (real_t)0;
}
