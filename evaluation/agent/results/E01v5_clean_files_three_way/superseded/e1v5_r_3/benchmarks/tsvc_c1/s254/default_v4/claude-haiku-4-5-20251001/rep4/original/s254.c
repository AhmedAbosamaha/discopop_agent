#include "data.h"

real_t kernel_s254(void)
{
    real_t x;
    x = b[LEN_1D-1];
    for (int i = 0; i < LEN_1D; i++) {
        a[i] = (b[i] + x) * (real_t).5;
        x = b[i];
    }
    return (real_t)0;
}
