#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int *prefix = (int*)malloc(LEN_1D * sizeof(int));
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: compute prefix sums to determine where each positive element goes
        int count = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                count++;
                prefix[i] = count;
            } else {
                prefix[i] = 0;
            }
        }
        // Second pass: write to correct positions (parallelizable - no loop-carried dependence)
        #pragma omp parallel for shared(prefix) 
        for (int i = 0; i < LEN_1D; i++) {
            if (prefix[i] > 0) {
                a[prefix[i] - 1] = b[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    free(prefix);
    return (real_t)0;
}
