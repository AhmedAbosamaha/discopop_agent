#include "data.h"

real_t kernel_s292(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Parallelize the inner loop by removing loop-carried dependencies through im1, im2.
        // Compute im1 and im2 directly from loop index i for each iteration.
        #pragma omp parallel for private(im1, im2)
        for (int i = 0; i < LEN_1D; i++) {
            int im1 = (i - 1 + LEN_1D) % LEN_1D;  // previous index with wraparound
            int im2 = (i - 2 + LEN_1D) % LEN_1D;  // two indices back with wraparound
            a[i] = (b[i] + b[im1] + b[im2]) * (real_t).333;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
