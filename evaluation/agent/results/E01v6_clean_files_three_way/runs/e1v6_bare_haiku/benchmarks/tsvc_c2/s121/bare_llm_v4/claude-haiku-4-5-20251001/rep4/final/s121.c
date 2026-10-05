#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s121(void)
{
    // Allocate a copy of array a to eliminate anti-dependence:
    // Sequential loop: iteration i reads a[i+1] (before iteration i+1 writes it).
    // Parallel version must read from a copy to break the anti-dependence.
    real_t *a_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Copy current state of a for reading in parallel
        memcpy(a_copy, a, LEN_1D * sizeof(real_t));

        // Parallelize inner loop:
        // Each iteration i reads a_copy[i+1] and b[i] (unchanged during loop),
        // writes a[i] (independent write location per iteration).
        // No loop-carried dependence: i reads a_copy[i+1], i+1 reads a_copy[i+2] (different).
        #pragma omp parallel for shared(a, a_copy, b)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = a_copy[i+1] + b[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_copy);
    return (real_t)0;
}
