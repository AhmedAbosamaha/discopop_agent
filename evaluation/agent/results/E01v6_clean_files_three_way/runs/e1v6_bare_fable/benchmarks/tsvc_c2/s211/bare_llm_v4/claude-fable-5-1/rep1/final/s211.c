#include <stdlib.h>
#include "data.h"

real_t kernel_s211(void)
{
    /* Scratch buffer holding the new values of b for one sweep. It grows
       with LEN_1D, so it lives on the heap, allocated once per call. */
    real_t *nb = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* Pass 1: new b values, read only from the OLD b (b[i+1]).
           nb[i] is exactly what the original stored into b[i]. */
#pragma omp parallel for default(none) shared(nb, b, d, e) schedule(static)
        for (int i = 1; i < LEN_1D - 1; i++) {
            nb[i] = b[i + 1] - e[i] * d[i];
        }

        /* a[1] reads b[0], which the original loop never modifies. */
        a[1] = b[0] + c[1] * d[1];

        /* Pass 2: a[i] uses the NEW b[i-1] (= nb[i-1]); commit b. */
#pragma omp parallel for default(none) shared(nb, a, b, c, d) schedule(static)
        for (int i = 2; i < LEN_1D - 1; i++) {
            a[i] = nb[i - 1] + c[i] * d[i];
            b[i - 1] = nb[i - 1];
        }
        b[LEN_1D - 2] = nb[LEN_1D - 2];

        dummy(a, b, c, d, e);
    }

    free(nb);
    return (real_t)0;
}
