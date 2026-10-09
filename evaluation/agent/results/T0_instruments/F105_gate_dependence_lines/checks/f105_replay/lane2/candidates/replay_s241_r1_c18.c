#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s241(void)
{
    real_t *a_old = malloc(sizeof(real_t) * (LEN_1D - 1));

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D-1; i++) {
            a_old[i] = a[i+1];
        }
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] * c[i  ] * d[i];
        }
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = a[i] * a_old[i] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
