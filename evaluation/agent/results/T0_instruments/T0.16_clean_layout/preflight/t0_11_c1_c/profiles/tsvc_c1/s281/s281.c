#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int i = 0; i < LEN_1D; i++) {
        x = a[LEN_1D-i-1] + b[i] * c[i];
        a[i] = x-(real_t)1.0;
        b[i] = x;
    }
    return (real_t)0;
}
