#include "data.h"
#include <stdlib.h>

real_t kernel_k23(void)
{
    // Precompute c and d states at each iteration boundary
    real_t **c_states = (real_t **)malloc(iterations * sizeof(real_t *));
    real_t **d_states = (real_t **)malloc(iterations * sizeof(real_t *));

    for (int nl = 0; nl < iterations; nl++) {
        c_states[nl] = (real_t *)malloc(LEN_1D * sizeof(real_t));
        d_states[nl] = (real_t *)malloc(LEN_1D * sizeof(real_t));
        // Save current state of c and d
        for (long i = 0; i < LEN_1D; i++) {
            c_states[nl][i] = c[i];
            d_states[nl][i] = d[i];
        }
        // Advance dummy state for next iteration
        dummy(a, b, c, d, e);
    }

    // i-loop is now outermost and parallelizable
    for (long i = 1; i < LEN_1D; i++) {
        for (int nl = 0; nl < iterations; nl++) {
            u[i] += w[i] * c_states[nl][i];
            v[i] = x[i] * d_states[nl][i] + c_states[nl][i];
        }
    }

    // Free allocated memory
    for (int nl = 0; nl < iterations; nl++) {
        free(c_states[nl]);
        free(d_states[nl]);
    }
    free(c_states);
    free(d_states);

    return (real_t)0;
}
