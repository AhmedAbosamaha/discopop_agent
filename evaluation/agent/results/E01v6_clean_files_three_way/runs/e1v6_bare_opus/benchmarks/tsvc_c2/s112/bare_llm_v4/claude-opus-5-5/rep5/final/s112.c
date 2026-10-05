#include <stdlib.h>
#include "data.h"

real_t kernel_s112(void)
{
    /* The descending loop reads a[i] before iteration i-1 overwrites it,
       so every read sees the ORIGINAL a: only an anti-dependence (location
       reuse).  Compute all new values into a scratch buffer first, then
       store them back; each pass is fully independent. */
    real_t *t = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    if (!t) return (real_t)0;

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for schedule(static) shared(a, b, t)
        for (int i = 0; i <= LEN_1D - 2; i++) {
            t[i] = a[i] + b[i];
        }
        #pragma omp parallel for schedule(static) shared(a, t)
        for (int i = 0; i <= LEN_1D - 2; i++) {
            a[i+1] = t[i];
        }
        dummy(a, b, c, d, e);
    }
    free(t);
    return (real_t)0;
}
