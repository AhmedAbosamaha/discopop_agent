#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    int *prefix = malloc((LEN_1D + 1) * sizeof(int));

    // Compute prefix sum once (count of matching elements up to each position)
    prefix[0] = 0;
    for (int i = 0; i < LEN_1D; i++) {
        prefix[i+1] = prefix[i];
        if (b[i] > (real_t)0.) {
            prefix[i+1]++;
        }
    }

    for (int nl = 0; nl < iterations; nl++) {
        // Use precomputed prefix to parallelize the write loop
        #pragma omp parallel for shared(prefix) 
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[prefix[i]] = b[i];
            }
        }

        dummy(a, b, c, d, e);
    }

    free(prefix);
    return (real_t)0;
}
