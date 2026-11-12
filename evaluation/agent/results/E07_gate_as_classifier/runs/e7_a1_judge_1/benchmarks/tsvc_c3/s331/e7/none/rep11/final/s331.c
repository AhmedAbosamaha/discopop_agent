#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        j = -1;

        // First pass: identify indices where condition is true (parallelizable)
        int *match_indices = (int *)malloc(LEN_1D * sizeof(int));
        #pragma omp parallel for shared(match_indices) 
        for (int i = 0; i < LEN_1D; i++) {
            match_indices[i] = a[i] < (real_t)0. ? i : -1;
        }

        // Second pass: find maximum matching index (reduction)
        for (int i = 0; i < LEN_1D; i++) {
            if (match_indices[i] > j) {
                j = match_indices[i];
            }
        }
        free(match_indices);

        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }
    return j+1;
}
