#include "data.h"
#include <math.h>

real_t kernel_s314(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        x = a[0];
        for (int i = 0; i < LEN_1D; i++) {
            x = fmax(x, a[i]);
        }
        dummy(a, b, c, d, e, x);
    }
    return x;
}
