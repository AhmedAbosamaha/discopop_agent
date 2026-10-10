#include "data.h"
#include <stdlib.h>

real_t kernel_s252(void)
{
    real_t t;
    real_t *prod = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(prod) 
        for (int i = 0; i < LEN_1D; i++) {
            prod[i] = b[i] * c[i];
        }

        t = (real_t) 0.;
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = prod[i] + t;
            t = prod[i];
        }

        dummy(a, b, c, d, e);
    }

    free(prod);
    return (real_t)0;
}
