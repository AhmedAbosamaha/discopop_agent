#include "data.h"

real_t kernel_s1213(void)
{
    for (int i = 1; i < LEN_1D-1; i++) {
        a[i] = b[i-1]+c[i];
        b[i] = a[i+1]*d[i];
    }
    return (real_t)0;
}
