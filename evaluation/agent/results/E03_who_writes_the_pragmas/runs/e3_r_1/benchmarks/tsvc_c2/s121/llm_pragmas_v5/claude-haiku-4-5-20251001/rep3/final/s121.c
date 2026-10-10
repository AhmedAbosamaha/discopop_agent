#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    // Allocate temporary buffer once outside loop
    real_t *a_temp = malloc(LEN_1D * sizeof(real_t));

    // Single parallel region for entire computation: amortizes thread startup cost
    // across all 48 outer loop iterations and ~32K inner iterations
    #pragma omp parallel shared(a, b, a_temp)
    {
        for (int nl = 0; nl < iterations; nl++) {
            // Copy phase: parallelize across threads
            #pragma omp for
            for (int k = 0; k < LEN_1D; k++) {
                a_temp[k] = a[k];
            }

            // Compute phase: parallelize across threads
            // Reads from constant a_temp, writes to independent a[i] positions
            #pragma omp for
            for (int i = 0; i < LEN_1D-1; i++) {
                a[i] = a_temp[i+1] + b[i];
            }

            // Implicit barrier ensures a[] is updated before dummy() reads it
            // Dummy phase: run on single thread
            #pragma omp single
            {
                dummy(a, b, c, d, e);
            }
        }
    }

    free(a_temp);
    return (real_t)0;
}
