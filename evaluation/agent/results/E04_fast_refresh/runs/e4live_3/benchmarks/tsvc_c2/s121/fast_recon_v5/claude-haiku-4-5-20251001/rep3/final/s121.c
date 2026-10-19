#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    int j;
    // Allocate buffer for shifted array values outside the repeated loop
    real_t *a_shifted = (real_t *)malloc((LEN_1D-1) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Capture a[i+1] values before they're overwritten
        #pragma omp parallel for shared(a_shifted) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a_shifted[i] = a[i+1];
        }

        #pragma omp parallel for private(j) shared(a_shifted) 
        for (int i = 0; i < LEN_1D-1; i++) {
            j = i + 1;
            a[i] = a_shifted[i] + b[i];
        }

        dummy(a, b, c, d, e);
    }

    free(a_shifted);
    return (real_t)0;
}
