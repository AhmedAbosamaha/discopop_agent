#include "data.h"
#include <stdlib.h>

real_t kernel_s331(void)
{
    int j = -1;
    real_t chksum;
    real_t *a_copy = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a_copy) 
        for (int i = 0; i < LEN_1D; i++) {
            a_copy[i] = a[i];
        }
        int j_local = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a_copy[i] < (real_t)0.) {
                j_local = (i > j_local) ? i : j_local;
            }
        }
        chksum = (real_t) j_local;
        dummy(a, b, c, d, e, chksum);
        j = j_local;
    }
    free(a_copy);
    return j+1;
}
