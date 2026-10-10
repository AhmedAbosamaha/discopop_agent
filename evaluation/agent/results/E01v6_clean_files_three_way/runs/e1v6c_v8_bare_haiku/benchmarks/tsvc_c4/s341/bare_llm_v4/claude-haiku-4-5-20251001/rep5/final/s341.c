#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    // Allocate index array to remove loop-carried dependence on j
    int *idx = (int *)malloc(LEN_1D * sizeof(int));
    if (!idx) return (real_t)0;

    for (int nl = 0; nl < iterations; nl++) {
        // Sequential loop: compute output indices for elements where b[i] > 0
        // This captures the loop-carried dependence on j sequentially
        int j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                j++;
                idx[i] = j;
            } else {
                idx[i] = -1;  // mark non-qualifying elements
            }
        }

        // Parallel loop: write qualifying elements to a using precomputed indices
        // Each thread writes to a unique index (idx is strictly increasing for qualifying elements)
        // so there are no write-write races
        #pragma omp parallel for shared(idx, b, a)
        for (int i = 0; i < LEN_1D; i++) {
            if (idx[i] >= 0) {
                a[idx[i]] = b[i];
            }
        }

        dummy(a, b, c, d, e);
    }

    free(idx);
    return (real_t)0;
}
