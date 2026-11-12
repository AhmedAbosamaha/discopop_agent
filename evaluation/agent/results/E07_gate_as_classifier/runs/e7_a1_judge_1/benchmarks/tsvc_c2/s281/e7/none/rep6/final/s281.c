#include "data.h"
#include <stdlib.h>

real_t kernel_s281(void)
{
    real_t x;
    real_t* temp_a = malloc(LEN_1D * sizeof(real_t));
    real_t* temp_b = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            temp_a[i] = x-(real_t)1.0;
            temp_b[i] = x;
        }
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = temp_a[i];
            b[i] = temp_b[i];
        }
        dummy(a, b, c, d, e);
    }

    free(temp_a);
    free(temp_b);
    return (real_t)0;
}
