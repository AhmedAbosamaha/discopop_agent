#include "data.h"
#include <math.h>

real_t kernel_s316(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        x = a[0];
        for (int i = 1; i < LEN_1D; ++i) {
            x = fmin(x, a[i]);
        }
        dummy(a, b, c, d, e, x);
    }
    return x;
}
