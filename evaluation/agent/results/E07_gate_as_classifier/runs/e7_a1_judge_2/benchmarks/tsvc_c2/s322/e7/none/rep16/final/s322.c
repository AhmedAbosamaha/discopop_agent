#include "data.h"
#include <stdlib.h>

real_t kernel_s322(void)
{
    real_t *tmp_a = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        if (nl == 0) {
            #pragma omp parallel for shared(tmp_a) 
            for (int i = 0; i < LEN_1D; i++) {
                tmp_a[i] = a[i];
            }
        }
        for (int i = 2; i < LEN_1D; i++) {
            tmp_a[i] = tmp_a[i] + tmp_a[i - 1] * b[i] + tmp_a[i - 2] * c[i];
        }
        for (int i = 2; i < LEN_1D; i++) {
            a[i] = tmp_a[i];
        }
        dummy(a, b, c, d, e);
        for (int i = 0; i < LEN_1D; i++) {
            tmp_a[i] = a[i];
        }
    }
    free(tmp_a);
    return (real_t)0;
}
