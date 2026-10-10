#include "data.h"
#include <stdlib.h>

real_t kernel_s212(void)
{
    // Allocate snapshot buffer once, reused across all outer loop activations
    real_t *old_a = malloc(LEN_1D * sizeof(real_t));

    // Single parallel region encompassing all outer iterations eliminates
    // redundant thread pool creation/destruction overhead (was 48×, now 1×)
    #pragma omp parallel shared(a, b, c, d, old_a)
    {
        for (int nl = 0; nl < iterations; nl++) {
            // Parallelize snapshot: each iteration i reads a[i] once
            #pragma omp for
            for (int i = 0; i < LEN_1D; i++) {
                old_a[i] = a[i];
            }

            // Parallelize main computation: each iteration i reads old_a[i+1]
            // (snapshot), writes to distinct a[i], b[i]; no loop-carried
            // dependence since all reads see pre-loop a values
            #pragma omp for
            for (int i = 0; i < LEN_1D-1; i++) {
                a[i] *= c[i];
                b[i] += old_a[i + 1] * d[i];
            }

            // Implicit barrier after #pragma omp for; dummy must run
            // after all threads finish the writes
            #pragma omp single
            {
                dummy(a, b, c, d, e);
            }
        }
    }

    free(old_a);
    return (real_t)0;
}
