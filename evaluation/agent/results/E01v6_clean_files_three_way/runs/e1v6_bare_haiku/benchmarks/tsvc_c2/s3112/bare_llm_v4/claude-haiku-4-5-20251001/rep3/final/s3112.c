#include "data.h"

real_t kernel_s3112(void)
{
    real_t sum;
    real_t *b_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        /* Parallel prefix sum initialization */
        #pragma omp parallel for shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            b[i] = a[i];
        }

        /* Parallel prefix sum using doubling algorithm */
        for (int step = 1; step < LEN_1D; step *= 2) {
            #pragma omp parallel for shared(b, b_temp, step) schedule(static)
            for (int i = 0; i < LEN_1D; i++) {
                if (i >= step) {
                    /* Accumulate: b[i] gets sum of elements [0..i] */
                    b_temp[i] = b[i] + b[i - step];
                } else {
                    /* No change for first step elements */
                    b_temp[i] = b[i];
                }
            }

            /* Copy results back for next iteration */
            #pragma omp parallel for shared(b, b_temp) schedule(static)
            for (int i = 0; i < LEN_1D; i++) {
                b[i] = b_temp[i];
            }
        }

        /* Extract final sum from last element */
        sum = b[LEN_1D - 1];

        dummy(a, b, c, d, e);
    }

    free(b_temp);
    return sum;
}
