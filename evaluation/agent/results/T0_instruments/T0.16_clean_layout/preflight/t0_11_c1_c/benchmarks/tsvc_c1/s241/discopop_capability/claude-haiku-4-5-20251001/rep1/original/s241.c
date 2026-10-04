#include "data.h"

real_t kernel_s241(void)
{
    for (int i = 0; i < LEN_1D-1; i++) {
        a[i] = b[i] * c[i  ] * d[i];
        b[i] = a[i] * a[i+1] * d[i];
    }
    return (real_t)0;
}
