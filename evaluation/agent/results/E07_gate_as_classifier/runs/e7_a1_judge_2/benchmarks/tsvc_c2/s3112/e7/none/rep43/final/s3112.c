#include "data.h"
#include <stdlib.h>

real_t kernel_s3112(void)
{
    real_t sum;
    for (int nl = 0; nl < iterations; nl++) {
        sum = (real_t)0.0;

        // Compute prefix sums into temporary array
        real_t *prefix = (real_t *)malloc(LEN_1D * sizeof(real_t));
        if (LEN_1D > 0) {
            prefix[0] = a[0];
            for (int i = 1; i < LEN_1D; i++) {
                prefix[i] = prefix[i-1] + a[i];
            }

            // Write prefix sums to b (now parallel-friendly: no loop-carried deps)
            for (int i = 0; i < LEN_1D; i++) {
                b[i] = prefix[i];
            }

            sum = prefix[LEN_1D - 1];
        }

        free(prefix);
        dummy(a, b, c, d, e);
    }
    return sum;
}
