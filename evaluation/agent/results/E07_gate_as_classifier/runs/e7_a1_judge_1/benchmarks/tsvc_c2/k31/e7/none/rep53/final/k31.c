#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k31(void)
{
    // Allocate once to preserve u values across all nl iterations
    real_t *u_orig = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Save the current u values before the first loop modifies them
        memcpy(u_orig, u, LEN_1D * sizeof(real_t));

        // First loop: update u based on v
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += v[i + off] * c[i];
        }
        // Second loop: compute v using original u values (before this nl's updates)
        for (long i = 1; i < LEN_1D; i++) {
            v[i] = u_orig[i + far] * d[i] + c[i];
        }

        dummy(a, b, c, d, e);
    }

    free(u_orig);
    return (real_t)0;
}
