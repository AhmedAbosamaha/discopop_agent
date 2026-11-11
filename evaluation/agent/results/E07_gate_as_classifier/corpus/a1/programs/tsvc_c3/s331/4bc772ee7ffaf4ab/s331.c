#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    real_t *j_vals = (real_t *)malloc(iterations * sizeof(real_t));

    // Phase 1: scan array a to find last negative index for each iteration
    for (int nl = 0; nl < iterations; nl++) {
        int j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        j_vals[nl] = (real_t) j;
    }

    // Phase 2: call dummy for each computed j value
    for (int nl = 0; nl < iterations; nl++) {
        dummy(a, b, c, d, e, j_vals[nl]);
    }

    int j = (int) j_vals[iterations - 1];
    free(j_vals);
    return j+1;
}
