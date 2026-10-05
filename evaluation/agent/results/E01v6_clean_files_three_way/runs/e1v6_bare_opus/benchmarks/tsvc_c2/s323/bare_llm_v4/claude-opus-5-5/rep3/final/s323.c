#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* independent part: the products, staged in a[] and b[] */
        #pragma omp parallel for schedule(static) default(none) shared(a, b, c, d, e)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = c[i] * d[i];
            b[i] = c[i] * e[i];
        }
        /* true recurrence through b[i-1]: kept serial, same rounding order */
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[i-1] + a[i];
            b[i] = a[i] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
