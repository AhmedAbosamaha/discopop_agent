#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Mark valid elements (b[i] > 0) in parallel
        // Each thread independently checks its portion of b and sets valid[i]
        int *valid = malloc(LEN_1D * sizeof(int));
        #pragma omp parallel for shared(b, valid)
        for (int i = 0; i < LEN_1D; i++) {
            valid[i] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        // Phase 2: Compute prefix sums (positions) - serial but O(n) linear pass
        // position[i] = index in output array 'a' where b[i] should go (if valid)
        // Uses -1 as sentinel for invalid elements, maintaining correct positions
        int *position = malloc(LEN_1D * sizeof(int));
        position[0] = valid[0] ? 0 : -1;
        for (int i = 1; i < LEN_1D; i++) {
            if (valid[i]) {
                position[i] = position[i-1] + 1;
            } else {
                position[i] = position[i-1];
            }
        }

        // Phase 3: Copy valid elements to compacted array in parallel
        // No loop-carried dependence: each thread writes to a[position[i]]
        // where position[i] is pre-computed and unique per valid element
        #pragma omp parallel for shared(b, a, valid, position)
        for (int i = 0; i < LEN_1D; i++) {
            if (valid[i]) {
                a[position[i]] = b[i];
            }
        }

        // Compute final value of j (index of last valid element) for compatibility
        j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (valid[i]) {
                j = position[i];
            }
        }

        // Free temporary arrays (heap-allocated for large LEN_1D)
        free(valid);
        free(position);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
