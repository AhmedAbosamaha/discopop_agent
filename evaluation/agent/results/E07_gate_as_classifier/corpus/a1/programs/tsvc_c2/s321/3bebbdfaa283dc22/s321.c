#include "data.h"

real_t kernel_s321(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t prev = a[0];
        for (int i = 1; i < LEN_1D; i++) {
            a[i] += prev * b[i];
            prev = a[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
