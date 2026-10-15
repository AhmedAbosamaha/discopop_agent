#include <stdlib.h>
#include "data.h"

real_t kernel_s257(void)
{
    real_t *aa_last = (real_t *)malloc(LEN_2D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (int i = 1; i < LEN_2D; i++) {
            aa_last[i] = aa[LEN_2D-1][i];
            a[i] = aa_last[i] - a[i-1];
            #pragma omp parallel for firstprivate(i) 
            for (int j = 0; j < LEN_2D; j++) {
                aa[j][i] = aa[j][i] + bb[j][i] - a[i-1];
            }
        }
        dummy(a, b, c, d, e, aa, bb, cc);
    }

    free(aa_last);
    return (real_t)0;
}
