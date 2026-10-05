#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s112(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *a_old = malloc(LEN_1D * sizeof(real_t));
        memcpy(a_old, a, LEN_1D * sizeof(real_t));

        #pragma omp parallel for shared(a, b, a_old)
        for (int i = 0; i < LEN_1D - 1; i++) {
            a[i+1] = a_old[i] + b[i];
        }

        free(a_old);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
