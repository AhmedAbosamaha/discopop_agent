#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        int *pos = (int *)malloc(LEN_1D * sizeof(int));
        #pragma omp parallel for shared(pos) 
        for (int i = 0; i < LEN_1D; i++) {
            pos[i] = -1;
        }
        int count = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                pos[i] = count;
                count++;
            }
        }
        #pragma omp parallel for shared(pos) 
        for (int i = 0; i < LEN_1D; i++) {
            if (pos[i] >= 0) {
                a[pos[i]] = b[i];
            }
        }
        free(pos);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
