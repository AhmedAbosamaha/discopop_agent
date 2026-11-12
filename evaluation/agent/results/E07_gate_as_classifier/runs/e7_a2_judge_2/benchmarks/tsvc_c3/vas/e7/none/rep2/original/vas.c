#include "data.h"

real_t kernel_vas(int * __restrict__ ip)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            a[ip[i]] = b[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
