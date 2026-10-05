#include <stdlib.h>
#include "data.h"

real_t kernel_s243(void)
{
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for default(none) shared(a, a_old) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }
        #pragma omp parallel for default(none) shared(a, b, c, d, e, a_old) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            real_t t = b[i] + c[i  ] * d[i];
            a[i] = t;
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + a_old[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(a_old);
    return (real_t)0;
}
