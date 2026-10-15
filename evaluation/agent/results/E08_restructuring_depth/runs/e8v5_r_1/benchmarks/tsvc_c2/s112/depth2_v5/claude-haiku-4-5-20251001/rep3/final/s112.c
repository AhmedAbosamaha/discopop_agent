#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s112(void)
{
    real_t *temp = malloc(sizeof(real_t) * LEN_1D);
    real_t *a_next = malloc(sizeof(real_t) * LEN_1D);
    memcpy(a_next, a, sizeof(real_t) * LEN_1D);
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_next) 
        for (int i = LEN_1D - 2; i >= 0; i--) {
            a_next[i+1] = a[i] + b[i];
        }
        a_next[0] = a[0];
        #pragma omp parallel for shared(a_next) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = a_next[i];
        }
        dummy(a, b, c, d, e);
    }
    free(temp);
    free(a_next);
    return (real_t)0;
}
