#include "data.h"

real_t kernel_s322(void)
{
    for (int i = 2; i < LEN_1D; i++) {
        a[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
    }
    return (real_t)0;
}
