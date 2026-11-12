#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    real_t *temp = (real_t*)malloc(LEN_1D * sizeof(real_t));
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: mark positive elements (no dependence on j - parallelizable)
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                temp[i] = b[i];
            } else {
                temp[i] = -(real_t)1.0;  // sentinel: will be skipped by condition
            }
        }
        // Second pass: compact selected values into array a
        j = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (temp[i] > (real_t)0.) {
                a[j] = temp[i];
                j++;
            }
        }
        dummy(a, b, c, d, e);
    }
    free(temp);
    return (real_t)0;
}
