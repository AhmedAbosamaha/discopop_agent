#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s112(void)
{
    real_t *a_new = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = LEN_1D - 2; i >= 0; i--) {
            a_new[i+1] = a[i] + b[i];
        }
        a_new[0] = a[0];

        memcpy(a, a_new, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    free(a_new);
    return (real_t)0;
}
