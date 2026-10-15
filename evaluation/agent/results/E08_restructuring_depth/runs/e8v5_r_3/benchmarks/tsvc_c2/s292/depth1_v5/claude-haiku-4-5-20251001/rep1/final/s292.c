#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_s292(void)
{
    int *im1_idx = (int *)malloc(LEN_1D * sizeof(int));
    int *im2_idx = (int *)malloc(LEN_1D * sizeof(int));

    #pragma omp parallel for shared(im2_idx,im1_idx) 
    for (int i = 0; i < LEN_1D; i++) {
        im1_idx[i] = (i - 1 + LEN_1D) % LEN_1D;
        im2_idx[i] = (i - 2 + LEN_1D) % LEN_1D;
    }

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(im2_idx,im1_idx) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = (b[i] + b[im1_idx[i]] + b[im2_idx[i]]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }

    free(im1_idx);
    free(im2_idx);
    return (real_t)0;
}
