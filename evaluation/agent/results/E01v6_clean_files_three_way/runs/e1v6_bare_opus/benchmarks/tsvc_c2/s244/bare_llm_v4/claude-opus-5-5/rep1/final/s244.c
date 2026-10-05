#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* a[i+1] written by iteration i is overwritten by iteration i+1
           (its old value is read only to compute that dead store), so
           only the last such store survives: done after the loop. */
        #pragma omp parallel for schedule(static) default(none) shared(a, b, c, d)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d[LEN_1D-2];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
