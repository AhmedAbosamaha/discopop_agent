#include "data.h"

real_t kernel_s252(void)
{
    // Compute a for first iteration with original b, c
    #pragma omp parallel for 
    for (int i = 0; i < LEN_1D; i++) {
        if (i == 0) {
            a[i] = b[i] * c[i];
        } else {
            a[i] = b[i] * c[i] + b[i-1] * c[i-1];
        }
    }

    // Pipeline: dummy call for previous iteration, then compute next
    for (int nl = 1; nl < iterations; nl++) {
        dummy(a, b, c, d, e);
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            if (i == 0) {
                a[i] = b[i] * c[i];
            } else {
                a[i] = b[i] * c[i] + b[i-1] * c[i-1];
            }
        }
    }

    // Call dummy for final iteration
    dummy(a, b, c, d, e);

    return (real_t)0;
}
