#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    int* matches = (int*)malloc(LEN_1D * sizeof(int));

    for (int nl = 0; nl < iterations; nl++) {
        // First pass: check condition for each element (Do-All: each iteration writes to a different array element)
        #pragma omp parallel for shared(matches) 
        for (int i = 0; i < LEN_1D; i++) {
            matches[i] = (a[i] < (real_t)0.);
        }

        // Second pass: find the last index where condition was true
        j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (matches[i]) {
                j = i;
            }
        }

        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }

    free(matches);
    return j+1;
}
