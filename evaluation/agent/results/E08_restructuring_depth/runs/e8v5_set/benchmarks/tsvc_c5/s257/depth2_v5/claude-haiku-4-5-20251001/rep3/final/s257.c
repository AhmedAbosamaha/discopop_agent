#include <stdlib.h>
#include "data.h"

real_t kernel_s257(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t (*aa_new)[LEN_2D] = (real_t (*)[LEN_2D])malloc(LEN_2D * LEN_2D * sizeof(real_t));

        for (int j = 0; j < LEN_2D; j++) {
            for (int i = 0; i < LEN_2D; i++) {
                aa_new[j][i] = aa[j][i];
            }
        }

        // Pass 1: Compute a[] values sequentially (preserves cascading dependency)
        for (int i = 1; i < LEN_2D; i++) {
            a[i] = aa[LEN_2D-1][i] - a[i-1];
        }

        // Pass 2: Compute aa_new[][] in parallel (no inter-iteration dependencies now)
 #pragma omp parallel for firstprivate(aa_new) 
        for (int i = 1; i < LEN_2D; i++) {
            for (int j = 0; j < LEN_2D; j++) {
                aa_new[j][i] = (aa[j][i] - a[i-1]) + bb[j][i];
            }
        }

 #pragma omp parallel for shared(aa_new) 
        for (int j = 0; j < LEN_2D; j++) {
            for (int i = 0; i < LEN_2D; i++) {
                aa[j][i] = aa_new[j][i];
            }
        }

        free(aa_new);

        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
