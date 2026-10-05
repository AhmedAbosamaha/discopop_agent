#include <stdlib.h>
#include "data.h"

real_t kernel_s211(void)
{
    real_t *t = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        /* new b values, computed from the old b only */
        #pragma omp parallel for default(none) shared(t, b, d, e) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            t[i] = b[i + 1] - e[i] * d[i];
        }
        /* a uses the new b[i-1] (old b[0] for i == 1); then commit b */
        #pragma omp parallel for default(none) shared(t, a, b, c, d) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            real_t prev = (i == 1) ? b[0] : t[i - 1];
            a[i] = prev + c[i] * d[i];
            b[i] = t[i];
        }
        dummy(a, b, c, d, e);
    }
    free(t);
    return (real_t)0;
}
