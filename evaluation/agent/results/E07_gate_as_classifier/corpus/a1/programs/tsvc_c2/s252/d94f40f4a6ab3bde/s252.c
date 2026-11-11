#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            if (i == 0) {
                a[i] = b[i] * c[i];
            } else {
                a[i] = b[i] * c[i] + b[i-1] * c[i-1];
            }
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
