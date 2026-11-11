#include "data.h"

real_t kernel_s323(void)
{
    real_t* temp_b = (real_t*) malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 0; i < LEN_1D; i++) {
            temp_b[i] = b[i];
        }
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = temp_b[i-1] + c[i] * d[i];
        }
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = a[i] + c[i] * e[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp_b);
    return (real_t)0;
}
