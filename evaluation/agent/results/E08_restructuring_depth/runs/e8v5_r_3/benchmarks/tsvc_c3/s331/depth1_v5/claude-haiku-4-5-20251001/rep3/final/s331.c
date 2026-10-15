#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: identify negative elements (Do-All pattern)
        char *is_negative = malloc(LEN_1D * sizeof(char));
        #pragma omp parallel for shared(is_negative) 
        for (int i = 0; i < LEN_1D; i++) {
            is_negative[i] = (a[i] < (real_t)0.) ? 1 : 0;
        }

        // Second pass: find the last (maximum) index where condition is true
        int j_local = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (is_negative[i]) {
                j_local = i;
            }
        }
        j = j_local;

        free(is_negative);

        chksum = (real_t) j;
        dummy(a, b, c, d, e, chksum);
    }
    return j+1;
}
