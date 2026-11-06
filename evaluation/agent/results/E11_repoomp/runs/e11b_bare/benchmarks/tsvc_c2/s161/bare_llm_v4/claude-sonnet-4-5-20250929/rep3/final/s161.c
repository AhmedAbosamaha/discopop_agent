#include "data.h"
#include <string.h>
#include <stdlib.h>

real_t kernel_s161(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *new_c = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(new_c, c, LEN_1D * sizeof(real_t));

        #pragma omp parallel for shared(new_c, a, b, c, d, e)
        for (int i = 0; i < LEN_1D-1; ++i) {
            if (b[i] < (real_t)0.) {
                new_c[i+1] = a[i] + d[i] * d[i];
            } else {
                a[i] = c[i] + d[i] * e[i];
            }
        }

        memcpy(c, new_c, LEN_1D * sizeof(real_t));
        free(new_c);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
