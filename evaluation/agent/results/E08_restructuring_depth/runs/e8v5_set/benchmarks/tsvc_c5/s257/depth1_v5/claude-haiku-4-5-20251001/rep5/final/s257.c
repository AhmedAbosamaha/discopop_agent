#include "data.h"

real_t kernel_s257(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: compute all a[] values (sequential due to recurrence)
        for (int i = 1; i < LEN_2D; i++) {
            a[i] = aa[LEN_2D-1][i] - a[i-1];
        }

        // Second pass: update aa[][] using finalized a[] values
        #pragma omp parallel for 
        for (int i = 1; i < LEN_2D; i++) {
            for (int j = 0; j < LEN_2D; j++) {
                real_t temp_a = aa[j][i] - a[i-1];
                aa[j][i] = temp_a + bb[j][i];
            }
        }
        dummy(a, b, c, d, e, aa, bb, cc);
    }
    return (real_t)0;
}
