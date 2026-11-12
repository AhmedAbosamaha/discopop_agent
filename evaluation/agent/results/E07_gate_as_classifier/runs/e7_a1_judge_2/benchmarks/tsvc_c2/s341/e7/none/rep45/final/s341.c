#include "data.h"
#include <stdlib.h>

real_t kernel_s341(void)
{
    int *pos = (int *)malloc(LEN_1D * sizeof(int));
    for (int nl = 0; nl < iterations; nl++) {
        int count = 0;
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                pos[i] = count;
                count++;
            }
        }
        #pragma omp parallel for shared(pos) 
        for (int i = 0; i < LEN_1D; i++) {
            if (b[i] > (real_t)0.) {
                a[pos[i]] = b[i];
            }
        }
        dummy(a, b, c, d, e);
    }
    free(pos);
    return (real_t)0;
}
