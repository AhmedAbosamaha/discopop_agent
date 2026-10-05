#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        /* Allocate temporary array to store positions for scatter phase */
        int *count = (int *)malloc(LEN_1D * sizeof(int));

        /* Phase 1: Identify positive elements (parallel)
           Each thread marks if b[i] > 0 */
        #pragma omp parallel for shared(b, count)
        for (int i = 0; i < LEN_1D; i++) {
            count[i] = (b[i] > (real_t)0.) ? 1 : 0;
        }

        /* Phase 2: Compute prefix sum (serial)
           count[i] becomes the output position for element i if positive
           sum accumulates the total count of positive elements */
        int sum = 0;
        for (int i = 0; i < LEN_1D; i++) {
            int temp = count[i];
            count[i] = sum;
            sum += temp;
        }

        /* Phase 3: Scatter positive elements to output array (parallel)
           If b[i] is positive, place it at position count[i] in a */
        #pragma omp parallel for shared(a, b, count)
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[count[i]] = b[i];
            }
        }

        /* Set j to the index of the last positive element */
        j = sum - 1;
        free(count);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
