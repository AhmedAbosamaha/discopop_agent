#include "data.h"
#include <stdlib.h>

real_t kernel_s315(void)
{
    real_t x, chksum;
    int index;

    real_t *candidates = (real_t *)malloc(LEN_1D * sizeof(real_t));
    int *indices = (int *)malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(indices,candidates) 
        for (int i = 0; i < LEN_1D; ++i) {
            candidates[i] = a[i];
            indices[i] = i;
        }

        x = candidates[0];
        index = indices[0];
        for (int i = 1; i < LEN_1D; ++i) {
            if (candidates[i] > x) {
                x = candidates[i];
                index = indices[i];
            }
        }

        chksum = x + (real_t) index;
        dummy(a, b, c, d, e, chksum);
    }

    free(candidates);
    free(indices);

    return index + x + 1;
}
