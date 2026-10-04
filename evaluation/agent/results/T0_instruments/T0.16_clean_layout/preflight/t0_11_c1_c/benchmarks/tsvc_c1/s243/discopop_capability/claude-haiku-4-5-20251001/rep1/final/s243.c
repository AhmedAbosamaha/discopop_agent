#include "data.h"

real_t kernel_s243(void)
{
    for (int i = 0; i < LEN_1D-1; i++) {
        a[i] = b[i] + c[i  ] * d[i];
        b[i] = a[i] + d[i  ] * e[i];
        a[i] = b[i] + a[i+1] * d[i];
    }
    return (real_t)0;
}
