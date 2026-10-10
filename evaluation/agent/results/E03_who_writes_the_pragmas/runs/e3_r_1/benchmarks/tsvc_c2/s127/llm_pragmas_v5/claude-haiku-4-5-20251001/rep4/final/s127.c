#include "data.h"

real_t kernel_s127(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for schedule(static)
        for (int i = 0; i < LEN_1D/2; i++) {
            int j0 = 2*i;
            int j1 = 2*i + 1;
            a[j0] = b[i] + c[i] * d[i];
            a[j1] = b[i] + d[i] * e[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
