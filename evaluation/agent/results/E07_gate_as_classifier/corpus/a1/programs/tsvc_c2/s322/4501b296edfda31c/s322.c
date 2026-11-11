#include "data.h"
#include <stdlib.h>

real_t kernel_s322(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* b_local = (real_t*) malloc(LEN_1D * sizeof(real_t));
        real_t* c_local = (real_t*) malloc(LEN_1D * sizeof(real_t));

        #pragma omp parallel for shared(b_local,c_local) 
        for (int j = 0; j < LEN_1D; j++) {
            b_local[j] = b[j];
            c_local[j] = c[j];
        }

        for (int i = 2; i < LEN_1D; i++) {
            a[i] = a[i] + a[i - 1] * b_local[i] + a[i - 2] * c_local[i];
        }

        free(b_local);
        free(c_local);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
