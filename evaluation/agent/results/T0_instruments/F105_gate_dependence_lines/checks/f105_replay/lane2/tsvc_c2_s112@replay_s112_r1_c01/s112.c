#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s112(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* temp = (real_t*)malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(temp) 
        for (int i = 0; i < LEN_1D - 1; i++) {
            temp[i+1] = a[i] + b[i];
        }
        memcpy(&a[1], &temp[1], (LEN_1D - 1) * sizeof(real_t));
        free(temp);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
