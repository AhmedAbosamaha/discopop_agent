#include "data.h"

real_t kernel_s257(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_2D; i++) {
            real_t prev_a = a[i-1];
            #pragma omp parallel for firstprivate(prev_a,i) 
            for (int j = 0; j < LEN_2D; j++) {
                real_t a_j = aa[j][i] - prev_a;
                aa[j][i] = a_j + bb[j][i];
            }
            a[i] = aa[LEN_2D-1][i] - bb[LEN_2D-1][i];
        }
        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
