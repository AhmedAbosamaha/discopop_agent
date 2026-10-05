#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s243(void)
{
    /* Heap-allocated snapshot of a[] as it was before the inner loop of
     * this pass modified it.  Sized LEN_1D since it grows with the
     * problem size, so it must not live on the stack. */
    real_t *olda = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        /* Snapshot a[] before this pass's updates: in the original
         * sequential order, the read of a[i+1] inside the loop always
         * saw the value a[i+1] had before this pass touched it (since
         * iteration i+1 runs after iteration i).  Capturing that value
         * here lets every iteration below read it independently of
         * execution order. */
        memcpy(olda, a, sizeof(real_t) * LEN_1D);

        #pragma omp parallel for default(none) shared(a, b, c, d, e, olda)
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = b[i] + c[i  ] * d[i];
            b[i] = a[i] + d[i  ] * e[i];
            a[i] = b[i] + olda[i+1] * d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(olda);
    return (real_t)0;
}
