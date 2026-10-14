#include "data.h"
#include <stdlib.h>

real_t kernel_s2251(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Save snapshot of b to avoid inter-iteration dependence
        real_t *old_b = (real_t *)malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(old_b) 
        for (int i = 0; i < LEN_1D; i++) {
            old_b[i] = b[i];
        }

        // Allocate temporary array for pre-computed s values
        real_t *s_seq = (real_t *)malloc(LEN_1D * sizeof(real_t));

        // Phase 1: Compute all s values using saved snapshot of b and c
        s_seq[0] = (real_t)0.0;
        #pragma omp parallel for shared(s_seq,old_b) 
        for (int i = 1; i < LEN_1D; i++) {
            s_seq[i] = old_b[i - 1] + c[i - 1];
        }

        // Phase 2: Compute a independently using pre-computed s_seq
        #pragma omp parallel for shared(s_seq) 
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = s_seq[i] * e[i];
        }

        // Phase 3: Update b independently using computed a
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = a[i] + d[i];
        }

        free(old_b);
        free(s_seq);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
