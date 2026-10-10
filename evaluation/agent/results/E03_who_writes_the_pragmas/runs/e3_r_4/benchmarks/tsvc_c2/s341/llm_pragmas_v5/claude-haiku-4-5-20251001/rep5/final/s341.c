#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int *prefix = (int *)malloc(LEN_1D * sizeof(int));

    // Compute prefix sum once (independent of outer loop iterations)
    int count = 0;
    for (int i = 0; i < LEN_1D; i++) {
        prefix[i] = count;
        if (b[i] > (real_t)0.) {
            count++;
        }
    }

    for (int nl = 0; nl < iterations; nl++) {
        // Parallel loop: each thread writes its element to the correct position
        #pragma omp parallel for shared(prefix, b, a)
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
