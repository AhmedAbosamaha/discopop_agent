#include "data.h"
#include <stdlib.h>

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        real_t* temp_a = malloc(LEN_1D * sizeof(real_t));
        real_t* temp_b = malloc(LEN_1D * sizeof(real_t));

        for (int i = 0; i < LEN_1D; i++) {
            x = a[LEN_1D-i-1] + b[i] * c[i];
            temp_a[i] = x-(real_t)1.0;
            temp_b[i] = x;
        }
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = temp_a[i];
            b[i] = temp_b[i];
        }

        free(temp_a);
        free(temp_b);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
