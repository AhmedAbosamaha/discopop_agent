#include "data.h"
#include <math.h>

real_t kernel_s314(void)
{
    real_t x_return;
    for (int nl = 0; nl < iterations; nl++) {
        real_t x = a[0];
        #pragma omp parallel for reduction(max:x) 
        for (int i = 1; i < LEN_1D; i++) {
            x = fmax(x, a[i]);
        }
        x_return = x;
        dummy(a, b, c, d, e, x);
    }
    return x_return;
}
