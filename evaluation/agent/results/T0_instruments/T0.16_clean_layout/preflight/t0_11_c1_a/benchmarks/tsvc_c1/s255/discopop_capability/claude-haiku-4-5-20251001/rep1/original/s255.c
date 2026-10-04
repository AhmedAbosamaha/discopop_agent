#include "data.h"

real_t kernel_s255(void)
{
    real_t x, y;
    x = b[LEN_1D-1];
    y = b[LEN_1D-2];
    for (int i = 0; i < LEN_1D; i++) {
        a[i] = (b[i] + x + y) * (real_t).333;
        y = x;
        x = b[i];
    }
    return (real_t)0;
}
