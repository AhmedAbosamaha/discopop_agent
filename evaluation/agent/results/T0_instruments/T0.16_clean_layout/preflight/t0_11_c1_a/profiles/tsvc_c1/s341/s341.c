#include "data.h"

real_t kernel_s341(void)
{
    int j;
    j = -1;
    for (int i = 0; i < LEN_1D; i++) {
        if (b[i] > (real_t)0.) {
            j++;
            a[j] = b[i];
        }
    }
    return (real_t)0;
}
