#include "data.h"

real_t kernel_s316(void)
{
    real_t x = 0;
    for (int nl = 0; nl < iterations; nl++) {
        x = a[0];
        for (int i = 1; i < LEN_1D; ++i) {
            if (a[i] < x) {
                x = a[i];
            }
        }
        dummy(a, b, c, d, e, x);
    }
    return x;
}
