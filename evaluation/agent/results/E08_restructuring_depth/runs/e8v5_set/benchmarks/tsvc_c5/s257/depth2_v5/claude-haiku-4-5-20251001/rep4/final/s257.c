#include "data.h"
#include <stdlib.h>

real_t kernel_s257(void)
{
    // Allocate temporary array to decouple a computation from loop iterations
    real_t *a_temp = (real_t *)malloc(LEN_2D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        // Step 1: Compute new a values sequentially (carries recurrence on a)
        // Initialize a_temp[0] with current value, then compute recurrence through a_temp
        a_temp[0] = a[0];
        for (int i = 1; i < LEN_2D; i++) {
            a_temp[i] = aa[LEN_2D-1][i] - a_temp[i-1];
        }

        // Step 2: Update aa using the newly computed a_temp values
        // This loop has no internal loop-carried dependence and can be parallelized
        #pragma omp parallel for shared(a_temp) 
        for (int i = 1; i < LEN_2D; i++) {
            for (int j = 0; j < LEN_2D; j++) {
                aa[j][i] = aa[j][i] - a_temp[i-1] + bb[j][i];
            }
        }

        // Step 3: Copy computed a values back to a
        for (int i = 1; i < LEN_2D; i++) {
            a[i] = a_temp[i];
        }

        dummy(a, b, c, d, e, aa, bb, cc);
    }

    free(a_temp);
    return (real_t)0;
}
