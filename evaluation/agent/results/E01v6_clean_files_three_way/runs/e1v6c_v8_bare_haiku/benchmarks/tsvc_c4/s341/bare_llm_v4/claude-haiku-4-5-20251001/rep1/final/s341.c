#include "data.h"
#include <stdlib.h>
#include <stdbool.h>

real_t kernel_s341(void)
{
    int j;
    // Allocate boolean mask array once (reused across iterations)
    bool *mask = malloc(LEN_1D * sizeof(bool));

    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Parallel loop - identify positive elements
        // Each iteration checks one element independently
        #pragma omp parallel for shared(mask, b)
        for (int i = 0; i < LEN_1D; i++) {
            mask[i] = (b[i] > (real_t)0.);
        }

        // Phase 2: Sequential compaction - copy positive elements using precomputed mask
        j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (mask[i]) {
                j++;
                a[j] = b[i];
            }
        }

        dummy(a, b, c, d, e);
    }

    free(mask);
    return (real_t)0;
}
