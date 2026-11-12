#include <stdlib.h>
#include "data.h"

real_t kernel_s121(void)
{
    real_t *temp_a = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            temp_a[i] = a[i];
        }

        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = temp_a[i + 1] + b[i];
        }

        dummy(a, b, c, d, e);
    }

    free(temp_a);
    return (real_t)0;
}
