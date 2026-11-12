#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s241(void)
{
    real_t *a_old = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        memcpy(a_old, a, LEN_1D * sizeof(real_t));

        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
            b[i] = a[i] * a_old[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_old);
    return (real_t)0;
}
