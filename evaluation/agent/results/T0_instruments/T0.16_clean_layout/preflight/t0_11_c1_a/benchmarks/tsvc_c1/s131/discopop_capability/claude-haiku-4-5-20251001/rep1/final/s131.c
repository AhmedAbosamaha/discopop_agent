#include "data.h"

real_t kernel_s131(void)
{
    int m  = 1;
    for (int i = 0; i < LEN_1D - 1; i++) {
        a[i] = a[i + m] + b[i];
    }
    return (real_t)0;
}
