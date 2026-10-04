#include "data.h"

real_t kernel_s424(void)
{
    int vl = 63;
    xx = flat_2d_array + vl;
    for (int i = 0; i < LEN_1D - 1; i++) {
        xx[i+1] = flat_2d_array[i] + a[i];
    }
    return (real_t)0;
}
