#include <stdlib.h>
#include "data.h"

real_t kernel_s341(void)
{
    int j;

    // Allocate temporary buffer once, outside the repeated outer loop
    real_t* temp = (real_t*)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        // Collect filtered elements sequentially (carries dependence on j)
        j = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                temp[j] = b[i];
                j++;
            }
        }

        // Copy result to output (no loop-carried dependencies—Do-All)
        #pragma omp parallel for firstprivate(j) shared(temp) 
        for (int i = 0; i < j; i++) {
            a[i] = temp[i];
        }

        dummy(a, b, c, d, e);
    }

    free(temp);
    return (real_t)0;
}
