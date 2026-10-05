#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Buffer initial values of a to eliminate WAR dependence on a[i+1]
        real_t *a_init = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *a_stmt3 = (real_t *)malloc(LEN_1D * sizeof(real_t));

        for (int i = 0; i < LEN_1D; ++i) {
            a_init[i] = a[i];
        }

        // Parallelize inner loop: each iteration now independent
        #pragma omp parallel for schedule(static) \
            private(i) \
            shared(a, b, c, d, a_init, a_stmt3, LEN_1D)
        for (int i = 0; i < LEN_1D-1; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
            // Use buffered initial value to read a[i+1], avoiding WAR dependence
            // Store result in temporary array to avoid write-write conflict
            a_stmt3[i] = b[i] + a_init[i+1] * d[i];
        }

        // Copy result of statement (3) for last element
        a[LEN_1D-1] = a_stmt3[LEN_1D-2];

        free(a_init);
        free(a_stmt3);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
