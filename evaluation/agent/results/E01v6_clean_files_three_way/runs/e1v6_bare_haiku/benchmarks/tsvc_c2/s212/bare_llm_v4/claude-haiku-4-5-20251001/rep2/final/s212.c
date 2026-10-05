#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    // Allocate temporary array to hold new a values
    // This allows parallelization by decoupling reads from writes
    real_t *a_new = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Parallel loop 1: compute new a values and update b
        // Each iteration i independently:
        //  - reads a[i+1] and c[i], d[i] from before any updates in this outer iteration
        //  - writes a_new[i] and b[i] to disjoint indices
        // shared(a, b, c, d, a_new): all arrays shared, accessed by loop index i
        #pragma omp parallel for shared(a, b, c, d, a_new)
        for (int i = 0; i < LEN_1D-1; i++) {
            a_new[i] = a[i] * c[i];
            b[i] += a[i + 1] * d[i];
        }

        // Parallel loop 2: copy computed a values back to a
        // Each iteration i independently writes to a[i] at a different index
        // shared(a, a_new): both arrays shared, accessed by loop index i
        #pragma omp parallel for shared(a, a_new)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_new[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_new);
    return (real_t)0;
}
