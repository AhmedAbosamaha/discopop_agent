#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s2251(void)
{
    real_t *b_saved = malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        real_t s;
        memcpy(b_saved, b, LEN_1D * sizeof(real_t));
        a[0] = 0.0 * e[0];
        #pragma omp parallel for shared(b_saved) 
        for (int i = 1; i < LEN_1D; i++) {
            a[i] = (b_saved[i-1] + c[i-1]) * e[i];
        }
        s = b_saved[LEN_1D-1] + c[LEN_1D-1];
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = a[i]+d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(b_saved);
    return (real_t)0;
}
