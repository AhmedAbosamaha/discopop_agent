#include "data.h"

real_t kernel_s233(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 1; i < LEN_2D; i++) {
            for (int j = 1; j < LEN_2D; j++) {
                aa[j][i] = aa[j-1][i] + cc[j][i];
            }
        }
        for (int i = 1; i < LEN_2D; i++) {
            #pragma omp parallel for firstprivate(i) 
            for (int j = 1; j < LEN_2D; j++) {
                bb[j][i] = bb[j][i-1] + cc[j][i];
            }
        }
        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
