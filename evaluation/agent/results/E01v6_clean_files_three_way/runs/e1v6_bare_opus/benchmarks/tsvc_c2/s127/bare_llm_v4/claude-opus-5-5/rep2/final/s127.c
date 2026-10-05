#include "data.h"

real_t kernel_s127(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for schedule(static) shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D/2; i++) {
            int j = 2 * i;
            a[j] = b[i] + c[i] * d[i];
            a[j + 1] = b[i] + d[i] * e[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
