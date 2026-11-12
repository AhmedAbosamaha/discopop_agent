#include "data.h"
#include <stdlib.h>

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *a_save = malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(a_save) 
        for (int j = 0; j < LEN_1D; ++j) {
            a_save[j] = a[j];
        }
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
            a[i+1] = b[i] + a_save[i+1] * d[i];
        }
        free(a_save);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
