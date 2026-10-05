#include "data.h"

real_t kernel_s281(void)
{
    real_t x;
    for (int nl = 0; nl < iterations; nl++) {
        /* Original loop couples index i with its mirror k = LEN_1D-1-i:
         * whichever is smaller is computed first from the pristine data,
         * the other reads that freshly written value. Different pairs
         * never share an index, so pairs can run in parallel; only the
         * two computations inside one pair must stay in that order. */
        int half = LEN_1D / 2;
        #pragma omp parallel for shared(a, b, c, half) schedule(static)
        for (int p = 0; p < half; p++) {
            int j = p;
            int k = LEN_1D - 1 - p;
            real_t xj = a[k] + b[j] * c[j];
            a[j] = xj - (real_t)1.0;
            b[j] = xj;
            real_t xk = a[j] + b[k] * c[k];
            a[k] = xk - (real_t)1.0;
            b[k] = xk;
        }
        if (LEN_1D % 2 == 1) {
            int m = LEN_1D / 2;
            x = a[m] + b[m] * c[m];
            a[m] = x - (real_t)1.0;
            b[m] = x;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
