#include "data.h"

void s152s(real_t a[LEN_1D], real_t b[LEN_1D], real_t c[LEN_1D], int i)
{
    a[i] += b[i] * c[i];
}

real_t kernel_s152(void)
{
    for (int i = 0; i < LEN_1D; i++) {
        b[i] = d[i] * e[i];
        s152s(a, b, c, i);
    }
    return (real_t)0;
}
