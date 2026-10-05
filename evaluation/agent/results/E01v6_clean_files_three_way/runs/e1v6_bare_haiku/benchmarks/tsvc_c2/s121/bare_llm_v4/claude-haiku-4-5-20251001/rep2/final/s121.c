#include "data.h"

real_t kernel_s121(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for private(j)
        for (int i = 0; i < LEN_1D-1; i++) {
            j = i + 1;
            a[i] = a[j] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
