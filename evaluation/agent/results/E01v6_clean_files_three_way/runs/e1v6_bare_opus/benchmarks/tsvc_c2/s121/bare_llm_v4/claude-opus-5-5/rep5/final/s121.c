#include <stdlib.h>
#include "data.h"

#define S121_BLK 1024

real_t kernel_s121(void)
{
    const int n = LEN_1D - 1;
    const int nb = (n + S121_BLK - 1) / S121_BLK;
    real_t *bnd = (real_t *)malloc((size_t)(nb > 0 ? nb : 1) * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        /* save the old value each block's last element reads across its boundary */
        for (int k = 0; k < nb; k++) {
            int hi = (k + 1) * S121_BLK;
            if (hi > n) hi = n;
            bnd[k] = a[hi];
        }
        #pragma omp parallel for default(none) shared(a, b, bnd) firstprivate(n, nb) schedule(static)
        for (int k = 0; k < nb; k++) {
            int lo = k * S121_BLK;
            int hi = lo + S121_BLK;
            if (hi > n) hi = n;
            for (int i = lo; i < hi - 1; i++) {
                a[i] = a[i + 1] + b[i];
            }
            a[hi - 1] = bnd[k] + b[hi - 1];
        }
        dummy(a, b, c, d, e);
    }
    free(bnd);
    return (real_t)0;
}
