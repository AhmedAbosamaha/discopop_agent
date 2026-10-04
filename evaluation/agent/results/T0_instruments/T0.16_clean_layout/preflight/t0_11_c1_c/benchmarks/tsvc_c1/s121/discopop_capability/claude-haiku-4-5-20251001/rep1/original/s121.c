#include "data.h"

real_t kernel_s121(void)
{
    int j;
    for (int i = 0; i < LEN_1D-1; i++) {
        j = i + 1;
        a[i] = a[j] + b[i];
    }
    return (real_t)0;
}
