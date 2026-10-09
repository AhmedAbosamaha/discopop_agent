#include "data.h"
#include <stdlib.h>

real_t kernel_s121(void)
{
    int j;
    real_t *temp = (real_t *)malloc((LEN_1D - 1) * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for private(j) shared(temp) 
        for (int i = 0; i < LEN_1D-1; i++) {
            j = i + 1;
            temp[i] = a[j] + b[i];
        }
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D-1; i++) {
            a[i] = temp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp);
    return (real_t)0;
}
