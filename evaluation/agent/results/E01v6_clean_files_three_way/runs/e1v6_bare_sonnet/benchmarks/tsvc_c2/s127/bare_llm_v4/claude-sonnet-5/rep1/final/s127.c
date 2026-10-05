#include "data.h"

real_t kernel_s127(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* j tracked 2*i and 2*i+1 in lockstep with i; made explicit so
         * each iteration of the inner loop touches disjoint elements of
         * a[] and can run independently of the others. */
        #pragma omp parallel for shared(a, b, c, d, e)
        for (int i = 0; i < LEN_1D/2; i++) {
            a[2*i] = b[i] + c[i] * d[i];
            a[2*i+1] = b[i] + d[i] * e[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
