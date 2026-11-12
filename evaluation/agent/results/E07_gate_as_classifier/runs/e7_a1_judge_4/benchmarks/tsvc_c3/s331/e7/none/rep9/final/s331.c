#include "data.h"

real_t kernel_s331(void)
{
    int j;
    real_t chksum;
    int* j_vals = (int*)malloc(iterations * sizeof(int));
    real_t* chksum_vals = (real_t*)malloc(iterations * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        j_vals[nl] = -1;
        for (int i = 0; i < LEN_1D; i++) {
            if (a[i] < (real_t)0.) {
                j_vals[nl] = i;
            }
        }
        chksum_vals[nl] = (real_t) j_vals[nl];
    }

    for (int nl = 0; nl < iterations; nl++) {
        j = j_vals[nl];
        chksum = chksum_vals[nl];
        dummy(a, b, c, d, e, chksum);
    }

    free(j_vals);
    free(chksum_vals);
    return j+1;
}
