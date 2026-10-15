#include "data.h"

real_t kernel_s254(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for 
        for (int i = 0; i < LEN_1D; i++) {
            int prev_i = (i == 0) ? (LEN_1D - 1) : (i - 1);
            a[i] = (b[i] + b[prev_i]) * (real_t).5;
        }
        long n = nl;
        long k = (n * 7919L + 13L) % LEN_1D;
        a[k] += (real_t)0.25; b[k] += (real_t)0.25; c[k] += (real_t)0.125;
        d[k] += (real_t)0.125; e[k] += (real_t)0.25;
        a[0] += (real_t)0.125; b[LEN_1D-1] += (real_t)0.125;
    }
    return (real_t)0;
}
