#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s243(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Save initial values of 'a' to break loop-carried dependence.
        // Iteration i reads a[i+1], which is written by iteration i+1.
        // By using a saved copy, each iteration reads from constant data.
        real_t *a_initial = malloc(LEN_1D * sizeof(real_t));
        memcpy(a_initial, a, LEN_1D * sizeof(real_t));

        #pragma omp parallel for shared(a, b, c, d, e, a_initial)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_initial[i+1] * d[i];
        }

        free(a_initial);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
