#include "data.h"

real_t kernel_s257(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_2D; i++) {
            a[i] = aa[LEN_2D-1][i] - a[i-1];
            #pragma omp parallel for firstprivate(i) 
            for (int j = 0; j < LEN_2D; j++) {
                aa[j][i] = aa[j][i] - a[i-1] + bb[j][i];
            }
        }
        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
