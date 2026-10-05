#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s243(void)
{
    /* Snapshot of a[] taken before each sweep: the original loop reads
       a[i+1] before iteration i+1 overwrites it, so every iteration must
       see the pre-sweep value.  Heap-allocated since it scales with LEN_1D. */
    real_t *a_old = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(a_old, a, (size_t)LEN_1D * sizeof(real_t));

        #pragma omp parallel for default(none) shared(a, b, c, d, e, a_old)
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
