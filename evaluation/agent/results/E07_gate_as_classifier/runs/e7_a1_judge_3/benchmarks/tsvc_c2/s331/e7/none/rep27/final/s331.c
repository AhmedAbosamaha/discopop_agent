#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int *j_results = (int*)malloc(iterations * sizeof(int));
    real_t chksum;
    for (int nl = 0; nl < iterations; nl++) {
        int j = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        j_results[nl] = j;
        chksum = (real_t) j;
        dummy(a, b, c, d, e);
    }
    int final_j = j_results[iterations - 1];
    free(j_results);
    return final_j + 1;
}
