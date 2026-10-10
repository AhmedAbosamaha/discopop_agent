#include "data.h"

real_t kernel_s316(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        x = a[0];
        #pragma omp parallel for reduction(min:x)
        for (int i = 1; i < LEN_1D; ++i) {
            x = (a[i] < x) ? a[i] : x;
        }
        dummy(a, b, c, d, e, x);
    }
    return x;
}
