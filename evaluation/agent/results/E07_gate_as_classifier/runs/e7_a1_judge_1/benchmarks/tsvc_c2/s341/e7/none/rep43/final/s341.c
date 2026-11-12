#include <stdlib.h>
#include "data.h"

real_t kernel_s341(void)
{
    int j;

    // Allocate index array once, outside the repeated outer loop to minimize overhead
    int* index = (int*)malloc(sizeof(int) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        // Compute output indices via prefix sum (sequential, carries dependence on j)
        j = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                index[i] = j;
                j++;
            } else {
                index[i] = -1;
            }
        }

        // Copy filtered elements (no loop-carried dependencies—Do-All)
        for (int i = 0; i < LEN_1D; i++) {
            if (index[i] >= 0) {
                a[index[i]] = b[i];
            }
        }

        dummy(a, b, c, d, e);
    }

    free(index);
    return (real_t)0;
}
