#include "data.h"
#include <stdlib.h>

real_t kernel_s112(void)
{
    real_t *temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = LEN_1D - 2; i >= 0; i--) {
            temp[i] = a[i] + b[i];
        }
        for (int i = LEN_1D - 2; i >= 0; i--) {
            a[i+1] = temp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp);
    return (real_t)0;
}
