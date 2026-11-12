#include "data.h"

static void compute_k23_inner_loop(void)
{
    for (long i = 1; i < LEN_1D; i++) {
        u[i] += w[i] * c[i];
        v[i] = x[i] * d[i] + c[i];
    }
}

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        compute_k23_inner_loop();
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
