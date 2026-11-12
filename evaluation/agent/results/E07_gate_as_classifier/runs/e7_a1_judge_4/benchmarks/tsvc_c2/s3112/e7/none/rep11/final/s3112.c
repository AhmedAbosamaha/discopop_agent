#include "data.h"
#include <stdlib.h>

real_t kernel_s3112(void)
{
    real_t sum;
    real_t *temp = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        sum = (real_t)0.0;
        for (int i = 0; i < LEN_1D; i++) {
            sum += a[i];
            temp[i] = sum;
        }
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = temp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp);
    return sum;
}
