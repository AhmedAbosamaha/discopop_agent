#include <stdlib.h>
#include "data.h"

real_t kernel_s121(void)
{
    /* Snapshot buffer: the original loop reads a[i+1] before iteration i+1
       overwrites it (anti-dependence).  Reading from a copy of a taken
       before the loop removes that dependence. */
    real_t *ta = (real_t *)malloc((size_t)LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for default(none) shared(a, ta) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            ta[i] = a[i];
        }
        #pragma omp parallel for default(none) shared(a, b, ta) schedule(static)
        for (int i = 0; i < LEN_1D-1; i++) {
            int j = i + 1;
            a[i] = ta[j] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    free(ta);
    return (real_t)0;
}
