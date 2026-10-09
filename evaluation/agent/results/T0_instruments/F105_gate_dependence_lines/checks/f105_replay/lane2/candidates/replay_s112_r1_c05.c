#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s112(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D - 1; i++) {
            int idx = LEN_1D - 2 - i;
            a[idx + 1] = a[idx] + b[idx];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
