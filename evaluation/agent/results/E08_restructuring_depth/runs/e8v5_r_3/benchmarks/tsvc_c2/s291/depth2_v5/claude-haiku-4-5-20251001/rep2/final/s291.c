#include "data.h"

real_t kernel_s291(void)
{
    static long n = 0;
    long n_start = n;

    for (int nl = 0; nl < iterations; nl++) {
        // Apply updates from previous iteration (stage 2 of pipeline)
        if (nl > 0) {
            long k_prev = ((n_start + nl - 1) * 7919L + 13L) % LEN_1D;
            a[k_prev] += (real_t)0.25; b[k_prev] += (real_t)0.25; c[k_prev] += (real_t)0.125;
            d[k_prev] += (real_t)0.125; e[k_prev] += (real_t)0.25;
            a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
        }

        // Compute a from current b (stage 1 of pipeline)
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            int prev = (i == 0) ? (LEN_1D - 1) : (i - 1);
            a[i] = (b[i] + b[prev]) * (real_t).5;
        }
    }

    // Apply final iteration's updates (epilog)
    if (iterations > 0) {
        long k_final = ((n_start + iterations - 1) * 7919L + 13L) % LEN_1D;
        a[k_final] += (real_t)0.25; b[k_final] += (real_t)0.25; c[k_final] += (real_t)0.125;
        d[k_final] += (real_t)0.125; e[k_final] += (real_t)0.25;
        a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
    }

    n = n_start + iterations;
    return (real_t)0;
}
