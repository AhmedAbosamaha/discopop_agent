#include <stdlib.h>
#include "data.h"

real_t kernel_s121(void)
{
    int j;
    /* Snapshot of a[] taken before each sweep: the original loop reads
       a[i+1] before iteration i+1 overwrites it (anti-dependence only),
       so reading from the snapshot makes every iteration independent. */
    real_t *tmp = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    if (tmp == NULL) return (real_t)0;

    for (int nl = 0; nl < iterations; nl++) {
#pragma omp parallel for default(none) shared(a, tmp) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            tmp[i] = a[i];
        }
#pragma omp parallel for default(none) shared(a, b, tmp) private(j) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            j = i + 1;
            a[i] = tmp[j] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    free(tmp);
    return (real_t)0;
}
