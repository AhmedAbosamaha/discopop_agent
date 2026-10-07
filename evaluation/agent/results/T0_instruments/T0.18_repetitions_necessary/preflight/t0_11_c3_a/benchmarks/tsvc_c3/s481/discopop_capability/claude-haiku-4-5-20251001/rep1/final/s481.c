#include <stdlib.h>
#include "data.h"

real_t kernel_s481(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for lastprivate(nl) 
        for (int i = 0; i < LEN_1D; i++) {
            if (d[i] < (real_t)0.) {
                exit (0);
            }
            a[i] += b[i] * c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
