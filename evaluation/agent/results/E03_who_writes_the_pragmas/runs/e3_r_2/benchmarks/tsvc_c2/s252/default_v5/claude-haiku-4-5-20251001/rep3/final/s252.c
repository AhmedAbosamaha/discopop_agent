#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    real_t t, s;
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for private(t,s) 
        for (int i = 0; i < LEN_1D; i++) {
            s = b[i] * c[i];
            t = (i == 0) ? (real_t) 0. : b[i-1] * c[i-1];
            a[i] = s + t;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
