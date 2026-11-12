#include "data.h"

static void update_u_v(long start, long end) {
    for (long i = start; i < end; i++) {
        u[i] += w[i] * c[i];
        v[i] = x[i] * d[i] + c[i];
    }
}

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        update_u_v(1, LEN_1D);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
