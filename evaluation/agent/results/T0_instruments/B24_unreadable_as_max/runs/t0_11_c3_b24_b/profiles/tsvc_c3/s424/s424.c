#include "data.h"

real_t kernel_s424(void)
{
    int vl = 63;
    xx = flat_2d_array + vl;
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D - 1; i++) {
            xx[i+1] = flat_2d_array[i] + a[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
