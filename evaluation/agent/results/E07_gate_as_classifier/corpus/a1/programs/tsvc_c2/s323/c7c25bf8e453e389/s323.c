#include <stdlib.h>
#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* sum_coeff = (real_t*) malloc(LEN_1D * sizeof(real_t));
        sum_coeff[0] = 0;
        for (int i = 1; i < LEN_1D; i++) {
            sum_coeff[i] = sum_coeff[i-1] + c[i] * (d[i] + e[i]);
        }
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = b[0] + sum_coeff[i-1] + c[i] * d[i];
            b[i] = b[0] + sum_coeff[i];
        }
        free(sum_coeff);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
