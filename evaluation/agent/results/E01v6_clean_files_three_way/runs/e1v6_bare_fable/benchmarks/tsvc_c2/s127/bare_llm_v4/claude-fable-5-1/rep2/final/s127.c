#include "data.h"

real_t kernel_s127(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* j was an induction variable: j == 2*i and 2*i+1 within iteration i. */
#pragma omp parallel for default(none) shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D/2; i++) {
            int j = 2 * i;
            a[j] = b[i] + c[i] * d[i];
            a[j + 1] = b[i] + d[i] * e[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
