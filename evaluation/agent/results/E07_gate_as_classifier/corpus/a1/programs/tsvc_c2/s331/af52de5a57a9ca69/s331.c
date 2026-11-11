#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int *j_results = (int*)malloc(iterations * sizeof(int));
    real_t *chksum_array = (real_t*)malloc(iterations * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        int j = -1;
        #pragma omp parallel for lastprivate(j) 
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j = i;
            }
        }
        j_results[nl] = j;
        chksum_array[nl] = (real_t) j;
    }

    for (int nl = 0; nl < iterations; nl++) {
        real_t chksum = chksum_array[nl];
        dummy(a, b, c, d, e);
    }

    int final_j = j_results[iterations - 1];
    free(j_results);
    free(chksum_array);
    return final_j + 1;
}
