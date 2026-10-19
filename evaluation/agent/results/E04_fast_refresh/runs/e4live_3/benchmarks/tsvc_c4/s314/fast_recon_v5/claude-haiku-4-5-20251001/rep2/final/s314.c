#include "data.h"
#include <math.h>

real_t kernel_s314(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        real_t x_local = a[0];
        #pragma omp parallel for reduction(max:x_local) 
        for (int i = 1; i < LEN_1D; i++) {
            x_local = fmax(x_local, a[i]);
        }
        dummy(a, b, c, d, e, x_local);
        x = x_local;
    }
    return x;
}
