#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s243(void)
{
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(a_old, a, sizeof(real_t) * LEN_1D);

        #pragma omp parallel for shared(a, b, c, d, e, a_old)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_old[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
