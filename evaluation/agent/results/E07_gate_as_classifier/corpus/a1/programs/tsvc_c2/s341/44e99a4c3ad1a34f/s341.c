#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    int *count = (int *)malloc(LEN_1D * sizeof(int));
    int *pos = (int *)malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: compute count array (1 if b[i] > 0, else 0) */
        #pragma omp parallel for shared(count) 
        for (int i = 0; i < LEN_1D; i++) {
            count[i] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        /* Pass 2: compute prefix sum for write positions */
        pos[0] = 0;
        for (int i = 1; i < LEN_1D; i++) {
            pos[i] = pos[i-1] + count[i-1];
        }

        /* Pass 3: write positive elements to a at precomputed positions */
        for (int i = 0; i < LEN_1D; i++) {
            if (count[i]) {
                a[pos[i]] = b[i];
            }
        }
        dummy(a, b, c, d, e);
    }

    free(count);
    free(pos);
    return (real_t)0;
}
