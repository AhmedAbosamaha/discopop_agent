#include "data.h"

real_t kernel_s121(void)
{
    int j;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for private(j)
        for (int i = LEN_1D-2; i >= 0; i--) {
            j = i + 1;
            a[i] = a[j] + b[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
