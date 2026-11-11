#include "data.h"

real_t kernel_s321(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_1D; i++) {
            real_t a_curr = a[i];
            real_t a_prev = a[i-1];
            real_t update = a_prev * b[i];
            a[i] = a_curr + update;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
