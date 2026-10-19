#include "data.h"
#include <math.h>

real_t kernel_s316(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        real_t x_local = a[0];
        #pragma omp parallel for reduction(min:x_local) 
        for (int i = 1; i < LEN_1D; ++i) {
            x_local = fmin(x_local, a[i]);
        }
        x = x_local;
        dummy(a, b, c, d, e, x);
    }
    return x;
}
