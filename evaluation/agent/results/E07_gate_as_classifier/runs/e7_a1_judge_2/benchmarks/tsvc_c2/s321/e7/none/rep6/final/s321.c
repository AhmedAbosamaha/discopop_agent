#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s321(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *temp = malloc(LEN_1D * sizeof(real_t));
        memcpy(temp, a, LEN_1D * sizeof(real_t));

        for (int i = 1; i < LEN_1D; i++) {
            temp[i] += a[i-1] * b[i];
        }

        memcpy(a, temp, LEN_1D * sizeof(real_t));
        free(temp);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
