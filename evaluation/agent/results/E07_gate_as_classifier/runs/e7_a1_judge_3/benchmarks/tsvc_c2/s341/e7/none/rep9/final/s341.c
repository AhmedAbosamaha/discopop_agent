#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    int *pos = (int *)malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: compute prefix sum for write positions (serial due to carry) */
        pos[0] = 0;
        for (int i = 1; i < LEN_1D; i++) {
            pos[i] = pos[i-1] + ((b[i-1] > (real_t)0.) ? 1 : 0);
        }

        /* Pass 2: write positive elements to a at precomputed positions */
        #pragma omp parallel for shared(pos) 
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[pos[i]] = b[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(pos);
    return (real_t)0;
}
