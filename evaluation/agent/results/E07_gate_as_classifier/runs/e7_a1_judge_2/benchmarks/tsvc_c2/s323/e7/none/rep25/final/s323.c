#include <stdlib.h>
#include "data.h"

real_t kernel_s323(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* new_b = (real_t*) malloc(LEN_1D * sizeof(real_t));
        for (int i = 0; i < LEN_1D; i++) {
            new_b[i] = b[i];
        }
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = new_b[i-1] + c[i] * d[i];
            new_b[i] = a[i] + c[i] * e[i];
        }
        for (int i = 1; i < LEN_1D; i++) {
            b[i] = new_b[i];
        }
        free(new_b);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
