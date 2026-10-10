#include "data.h"
#include <stdlib.h>

real_t kernel_s112(void)
{
    // Allocate temporary buffer to hold snapshot of 'a' for parallel reads
    real_t *a_orig = (real_t *)malloc(LEN_1D * sizeof(real_t));

    // Create a single parallel region spanning all outer iterations to amortize
    // thread startup cost across all work (~48 * 32000 iterations total)
    #pragma omp parallel shared(a, a_orig, b)
    {
        for (int nl = 0; nl < iterations; nl++) {
            // Parallel copy of 'a' to 'a_orig': all threads share this work
            // (implicit barrier at end of worksharing directive)
            #pragma omp for
            for (int j = 0; j < LEN_1D; j++) {
                a_orig[j] = a[j];
            }

            // Parallel computation of inner loop: each thread i reads a_orig[i]
            // and writes a[i+1] (unique per iteration, no race)
            // (implicit barrier at end of worksharing directive)
            #pragma omp for
            for (int i = LEN_1D - 2; i >= 0; i--) {
                a[i+1] = a_orig[i] + b[i];
            }

            // Serialize dummy() call (has static counter, must be sequential)
            // Explicit barrier after single-block to synchronize for next iteration
            #pragma omp single
            {
                dummy(a, b, c, d, e);
            }
            #pragma omp barrier
        }
    }

    free(a_orig);
    return (real_t)0;
}
