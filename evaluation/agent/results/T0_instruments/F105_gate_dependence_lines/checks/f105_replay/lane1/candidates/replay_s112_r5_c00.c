#include "data.h"
#include <stdlib.h>

real_t kernel_s112(void)
{
    real_t *temp = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D - 1; i++) {
            temp[i] = a[i] + b[i];
        }
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i+1] = temp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp);
    return (real_t)0;
}
