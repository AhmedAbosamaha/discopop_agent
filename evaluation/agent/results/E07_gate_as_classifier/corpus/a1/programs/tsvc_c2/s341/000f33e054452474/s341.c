#include <stdlib.h>
#include "data.h"

real_t kernel_s341(void)
{
    // Allocate temp buffer for qualified elements
    real_t *temp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Collect qualifying elements into temp buffer (sequential, no j dependence across b reads)
        int count = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                temp[count] = b[i];
                count++;
            }
        }

        // Copy collected elements to output array (parallelizable, independent writes)
        for (int i = 0; i < count; i++) {
            a[i] = temp[i];
        }

        dummy(a, b, c, d, e);
    }

    free(temp);
    return (real_t)0;
}
