#include "data.h"
#include <stdlib.h>

real_t kernel_s319(void)
{
    real_t sum;
    real_t *temp = (real_t *) malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        sum = 0.;
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = c[i] + d[i];
            b[i] = c[i] + e[i];
            temp[i] = a[i] + b[i];
        }
        #pragma omp parallel for shared(temp) reduction(+:sum) 
        for (int i = 0; i < LEN_1D; i++) {
            sum += temp[i];
        }
        dummy(a, b, c, d, e, sum);
    }

    free(temp);
    return sum;
}
