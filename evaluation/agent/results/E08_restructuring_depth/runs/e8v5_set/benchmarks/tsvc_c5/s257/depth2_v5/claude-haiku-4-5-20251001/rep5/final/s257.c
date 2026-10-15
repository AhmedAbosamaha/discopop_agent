#include "data.h"

real_t kernel_s257(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Fused Phase 1 and Phase 2: compute a[i], then update aa for that i
        for (int i = 1; i < LEN_2D; i++) {
            // Phase 1: Compute a[i] from aa[LEN_2D-1][i] and a[i-1]
            real_t a_final = aa[LEN_2D-1][i] - a[i-1];
            a[i] = a_final;

            // Phase 2: Update aa[j][i] using a[i-1] (from previous iteration)
            #pragma omp parallel for firstprivate(i) 
            for (int j = 0; j < LEN_2D; j++) {
                real_t a_temp = aa[j][i] - a[i-1];
                aa[j][i] = a_temp + bb[j][i];
            }
        }

        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
