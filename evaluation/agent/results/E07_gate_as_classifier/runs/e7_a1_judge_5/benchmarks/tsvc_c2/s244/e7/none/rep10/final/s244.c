#include "data.h"
#include <stdlib.h>

real_t kernel_s244(void)
{
    real_t *a_orig = malloc(LEN_1D * sizeof(real_t));
    real_t *temp_a = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* Save original a values before phase 1 modifies them */
        #pragma omp parallel for shared(a_orig) 
        for (int i = 0; i < LEN_1D; ++i) {
            a_orig[i] = a[i];
        }

        /* Phase 1: compute a[i] and update b[i] */
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }

        /* Phase 2: compute a[i+1] using original a values and updated b values */
        for (int i = 0; i < LEN_1D-1; ++i) {
            temp_a[i+1] = b[i] + a_orig[i+1] * d[i];
        }

        /* Restore final state: a[LEN_1D-1] comes from phase 2, rest from phase 1 */
        a[LEN_1D-1] = temp_a[LEN_1D-1];

        dummy(a, b, c, d, e);
    }

    free(temp_a);
    free(a_orig);
    return (real_t)0;
}
