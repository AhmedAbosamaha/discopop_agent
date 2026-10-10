#include "data.h"

real_t kernel_s171(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            a[i * inc] += b[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
