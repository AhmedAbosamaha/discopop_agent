#include "data.h"

real_t kernel_s257(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t a_tmp[LEN_2D];
        for (int i = 0; i < LEN_2D; i++) {
            a_tmp[i] = a[i];
        }
        for (int i = 1; i < LEN_2D; i++) {
            #pragma omp parallel for firstprivate(i) shared(a_tmp) 
            for (int j = 0; j < LEN_2D; j++) {
                real_t local_a = aa[j][i] - a_tmp[i-1];
                aa[j][i] = local_a + bb[j][i];
            }
            a_tmp[i] = aa[LEN_2D-1][i] - bb[LEN_2D-1][i];
        }
        for (int i = 1; i < LEN_2D; i++) {
            a[i] = a_tmp[i];
        }
        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
