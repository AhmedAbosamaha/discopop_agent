#include "data.h"

real_t kernel_s252(void)
{
    real_t s;
    for (int nl = 0; nl < iterations; nl++) {
        /* Handle first element sequentially */
        s = b[0] * c[0];
        a[0] = s;

        /* Parallelize remaining loop: a[i] = b[i]*c[i] + b[i-1]*c[i-1] */
        #pragma omp parallel for private(s)
        for (int i = 1; i < LEN_1D; i++) {
            s = b[i] * c[i];
            a[i] = s + b[i-1] * c[i-1];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
