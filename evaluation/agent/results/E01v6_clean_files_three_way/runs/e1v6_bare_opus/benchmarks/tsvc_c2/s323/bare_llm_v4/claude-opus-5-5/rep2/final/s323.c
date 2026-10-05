#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Independent part: the products, stored in a[i] / b[i] (both are
           overwritten below before anything else reads them). */
        #pragma omp parallel for schedule(static) default(none) shared(a, b, c, d, e)
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = c[i] * d[i];
            b[i] = c[i] * e[i];
        }
        /* True recurrence b[i-1] -> a[i] -> b[i]: kept serial, same
           rounding order as the original. b[0] is not written above. */
        real_t prev = b[0];
        for (int i = 1; i < LEN_1D; i++) {
            real_t ai = prev + a[i];
            a[i] = ai;
            prev = ai + b[i];
            b[i] = prev;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
