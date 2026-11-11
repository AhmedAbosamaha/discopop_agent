#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            long i_cur = i;
            u[i_cur] = u[i_cur] + w[i_cur] * c[i_cur];
        }
        for (long i = 1; i < LEN_1D; i++) {
            long i_cur = i;
            v[i_cur] = x[i_cur] * d[i_cur] + c[i_cur];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
