#include <stdlib.h>
#include "data.h"

real_t kernel_s121(void)
{
    real_t *temp = malloc((LEN_1D) * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel
        {
            #pragma omp for
            for (int i = 0; i < LEN_1D-1; i++) {
                int j = i + 1;
                temp[i] = a[j] + b[i];
            }
            #pragma omp for
            for (int i = 0; i < LEN_1D-1; i++) {
                a[i] = temp[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    free(temp);
    return (real_t)0;
}
