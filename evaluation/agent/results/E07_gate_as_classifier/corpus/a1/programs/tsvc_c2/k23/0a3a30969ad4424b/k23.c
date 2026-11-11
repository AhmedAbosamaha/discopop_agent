#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *w_local = w;
        real_t *c_local = c;
        real_t *x_local = x;
        real_t *d_local = d;
        for (long i = 1; i < LEN_1D; i++) {
            real_t tmp_u = w_local[i] * c_local[i];
            real_t tmp_v = x_local[i] * d_local[i] + c_local[i];
            u[i] += tmp_u;
            v[i] = tmp_v;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
