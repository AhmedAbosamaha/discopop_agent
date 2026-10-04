#include <stdlib.h>
#include "data.h"

real_t kernel_s211(void)
{
    real_t *t = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    /* new b values, computed from the old b only */
    #pragma omp parallel for schedule(static) default(none) shared(t, b, e, d)
    for (int i = 1; i < LEN_1D-1; i++) {
        t[i] = b[i + 1] - e[i] * d[i];
    }

    /* a[i] uses the updated b[i-1] (b[0] is never updated) */
    #pragma omp parallel for schedule(static) default(none) shared(t, a, b, c, d)
    for (int i = 1; i < LEN_1D-1; i++) {
        real_t bprev = (i == 1) ? b[0] : t[i - 1];
        a[i] = bprev + c[i] * d[i];
        b[i] = t[i];
    }

    free(t);
    return (real_t)0;
}
