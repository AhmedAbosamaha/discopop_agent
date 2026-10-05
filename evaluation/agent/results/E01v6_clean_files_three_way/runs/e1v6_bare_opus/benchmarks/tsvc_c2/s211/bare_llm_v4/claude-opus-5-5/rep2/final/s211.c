#include <stdlib.h>
#include "data.h"

real_t kernel_s211(void)
{
    real_t *tmp = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    if (!tmp) return (real_t)0;
    for (int nl = 0; nl < iterations; nl++) {
        /* new b values, computed from old b only */
        #pragma omp parallel for default(none) shared(tmp, b, d, e) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            tmp[i] = b[i + 1] - e[i] * d[i];
        }
        /* a uses new b[i-1] (tmp[i-1]; b[0] is never modified) */
        #pragma omp parallel for default(none) shared(tmp, a, b, c, d) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            real_t bp = (i == 1) ? b[0] : tmp[i - 1];
            a[i] = bp + c[i] * d[i];
            b[i] = tmp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
