#include "data.h"

real_t kernel_s482(void)
{
    for (int i = 0; i < LEN_1D; i++) {
        a[i] += b[i] * c[i];
        if (c[i] > b[i]) break;
    }
    return (real_t)0;
}
