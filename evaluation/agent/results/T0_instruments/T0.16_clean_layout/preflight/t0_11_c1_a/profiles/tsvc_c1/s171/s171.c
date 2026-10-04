#include "data.h"

real_t kernel_s171(void)
{
    for (int i = 0; i < LEN_1D; i++) {
        a[i * inc] += b[i];
    }
    return (real_t)0;
}
