#include <stdlib.h>
#include "data.h"

#define S121_BLK 4096

real_t kernel_s121(void)
{
    const int n = LEN_1D - 1;               /* iterations i = 0 .. n-1 */
    const int nb = (n + S121_BLK - 1) / S121_BLK;
    real_t *edge = (real_t *)malloc((size_t)(nb > 0 ? nb : 1) * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* save the old value each block reads just past its end */
        for (int k = 0; k < nb; k++) {
            int hi = (k + 1) * S121_BLK;
            if (hi > n) hi = n;
            edge[k] = a[hi];
        }
#pragma omp parallel for shared(a, b, edge) schedule(static)
        for (int k = 0; k < nb; k++) {
            int lo = k * S121_BLK;
            int hi = lo + S121_BLK;
            if (hi > n) hi = n;
            for (int i = lo; i < hi - 1; i++)
                a[i] = a[i + 1] + b[i];
            a[hi - 1] = edge[k] + b[hi - 1];
        }
        dummy(a, b, c, d, e);
    }
    free(edge);
    return (real_t)0;
}
