#include "data.h"

real_t kernel_s321(void)
{
    for (int i = 1; i < LEN_1D; i++) {
        a[i] += a[i-1] * b[i];
    }
    return (real_t)0;
}
