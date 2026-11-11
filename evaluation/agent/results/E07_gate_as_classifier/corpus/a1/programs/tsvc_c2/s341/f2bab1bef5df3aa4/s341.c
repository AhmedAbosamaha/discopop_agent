#include <stdlib.h>
#include "data.h"

real_t kernel_s341(void)
{
    // Allocate prefix array once outside the loop to avoid repeated malloc/free overhead
    int *prefix = (int *)malloc((LEN_1D + 1) * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        // Compute prefix sum: for each position i, count how many preceding elements satisfy b[i] > 0
        prefix[0] = 0;
        for (int i = 0; i < LEN_1D; i++) {
            prefix[i + 1] = prefix[i];
            if (b[i] > (real_t)0.) {
                prefix[i + 1]++;
            }
        }

        // Write qualifying elements to their computed positions (no loop-carried dependence)
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
