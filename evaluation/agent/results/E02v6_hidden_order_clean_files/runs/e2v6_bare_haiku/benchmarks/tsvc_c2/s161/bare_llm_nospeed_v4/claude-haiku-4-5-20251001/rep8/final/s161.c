#include "data.h"
#include <stdlib.h>

real_t kernel_s161(void)
{
    // Allocate temporary arrays for restructured two-pass algorithm
    // Pass 1 computes both branches independently, Pass 2 selects based on condition
    real_t *temp_a = malloc(sizeof(real_t) * (LEN_1D-1));
    real_t *temp_c = malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        // Pass 1: Compute temporary values for both branches
        // All iterations independent: each writes to different array indices
        #pragma omp parallel for shared(a, b, c, d, e, temp_a, temp_c)
        for (int i = 0; i < LEN_1D-1; ++i) {
            temp_a[i] = c[i] + d[i] * e[i];        // else branch: a[i] = c[i] + d[i] * e[i]
            temp_c[i+1] = a[i] + d[i] * d[i];      // if branch: c[i+1] = a[i] + d[i] * d[i]
        }

        // Pass 2: Select which computed value to use based on condition
        // All iterations independent: each writes to a[i] or c[i+1] (different indices per iteration)
        #pragma omp parallel for shared(a, b, c, d, e, temp_a, temp_c)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                c[i+1] = temp_c[i+1];               // if branch: use computed c[i+1]
            } else {
                a[i] = temp_a[i];                   // else branch: use computed a[i]
            }
        }

        dummy(a, b, c, d, e);
    }

    free(temp_a);
    free(temp_c);

    return (real_t)0;
}
