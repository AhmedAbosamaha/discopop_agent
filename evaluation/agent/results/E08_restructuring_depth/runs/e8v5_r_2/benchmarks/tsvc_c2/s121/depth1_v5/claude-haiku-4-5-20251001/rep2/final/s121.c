#include <stdlib.h>
#include "data.h"

real_t kernel_s121(void)
{
    real_t *temp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    // Phase 1: Prefetch for iteration 0
    #pragma omp parallel for shared(temp) 
    for (int i = 0; i < LEN_1D-1; i++) {
        temp[i] = a[i+1];
    }

    // Pipelined iterations: read a for next iteration while computing current
    for (int nl = 0; nl < iterations - 1; nl++) {
        // Compute phase for current iteration
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = temp[i] + b[i];
        }
        // Prefetch phase for next iteration
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D-1; i++) {
            temp[i] = a[i+1];
        }
        dummy(a, b, c, d, e);
    }

    // Final iteration: compute without prefetch
    for (int i = 0; i < LEN_1D-1; i++) {
        a[i] = temp[i] + b[i];
    }
    dummy(a, b, c, d, e);

    free(temp);
    return (real_t)0;
}
