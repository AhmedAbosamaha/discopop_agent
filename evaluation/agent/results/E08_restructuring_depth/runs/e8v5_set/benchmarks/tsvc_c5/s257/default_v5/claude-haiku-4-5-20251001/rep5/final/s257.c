#include "data.h"

real_t kernel_s257(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_2D; i++) {
            real_t aa_last_old = aa[LEN_2D-1][i];
            #pragma omp parallel for firstprivate(i) 
            for (int j = 0; j < LEN_2D; j++) {
                real_t a_tmp = aa[j][i] - a[i-1];
                aa[j][i] = a_tmp + bb[j][i];
            }
            a[i] = aa_last_old - a[i-1];
        }
        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
