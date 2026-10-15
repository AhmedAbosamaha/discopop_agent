#include "data.h"

real_t kernel_s257(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_2D; i++) {
            real_t a_temp[LEN_2D];
            #pragma omp parallel for firstprivate(i) shared(a_temp) 
            for (int j = 0; j < LEN_2D; j++) {
                a_temp[j] = aa[j][i] - a[i-1];
            }
            #pragma omp parallel for firstprivate(i) shared(a_temp) 
            for (int j = 0; j < LEN_2D; j++) {
                aa[j][i] = a_temp[j] + bb[j][i];
            }
            a[i] = a_temp[LEN_2D-1];
        }
        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
