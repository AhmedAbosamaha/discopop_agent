#include "data.h"
#include <stdlib.h>

real_t kernel_s244(void)
{
    // Allocate scratch array to hold initial values of a for each outer iteration
    real_t *a_old = (real_t *)malloc(LEN_1D * sizeof(real_t));

    // Initialize a_old with the initial state of a before the loop
    for (int i = 0; i < LEN_1D; ++i) {
        a_old[i] = a[i];
    }

    for (int nl = 0; nl < iterations; nl++) {
        // Compute a[i] and b[i] for each iteration (no WAW conflicts)
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }

        // Compute the last element of a using the saved a_old values
        a[LEN_1D-1] = b[LEN_1D-2] + a_old[LEN_1D-1] * d[LEN_1D-2];

        dummy(a, b, c, d, e);

        // Save the updated state of array a for the next iteration
        #pragma omp parallel for shared(a_old) 
        for (int i = 0; i < LEN_1D; ++i) {
            a_old[i] = a[i];
        }
    }

    free(a_old);
    return (real_t)0;
}
