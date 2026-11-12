#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s322(void)
{
    real_t* temp = (real_t*)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        memcpy(temp, a, LEN_1D * sizeof(real_t));
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = temp[i] + temp[i - 1] * b[i] + temp[i - 2] * c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp);
    return (real_t)0;
}
