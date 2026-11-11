#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int j;
    real_t chksum;

    // Allocate arrays to store j and chksum for each iteration
    int *j_array = (int *)malloc(iterations * sizeof(int));
    real_t *chksum_array = (real_t *)malloc(iterations * sizeof(real_t));

    // First pass: compute j and chksum for all iterations (reading original a[])
    for (int nl = 0; nl < iterations; nl++) {
        j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        j_array[nl] = j;
        chksum_array[nl] = (real_t) j;
    }

    // Second pass: call dummy for each iteration (preserves order and side effects)
    for (int nl = 0; nl < iterations; nl++) {
        dummy(a, b, c, d, e, chksum_array[nl]);
    }

    // Get the final j value
    j = j_array[iterations - 1];

    // Free allocated memory
    free(j_array);
    free(chksum_array);

    return j + 1;
}
