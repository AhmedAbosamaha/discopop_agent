#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s322(void)
{
    real_t *a_new = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a, b, c, a_new)
        for (int i = 2; i < LEN_1D; i++) {
            a_new[i] = a[i] + a[i - 1] * b[i] + a[i - 2] * c[i];
        }

        memcpy(a, a_new, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    free(a_new);
    return (real_t)0;
}
