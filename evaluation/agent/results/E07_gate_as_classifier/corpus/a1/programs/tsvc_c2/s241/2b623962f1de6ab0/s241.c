#include <stdlib.h>
#include "data.h"

real_t kernel_s241(void)
{
    real_t *a_old = (real_t *)malloc((LEN_1D) * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D-1; i++) {
            a_old[i+1] = a[i+1];
            a[i] = b[i] * c[i  ] * d[i];
        }
        for (int i = 0; i < LEN_1D-1; i++) {
            b[i] = a[i] * a_old[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_old);
    return (real_t)0;
}
