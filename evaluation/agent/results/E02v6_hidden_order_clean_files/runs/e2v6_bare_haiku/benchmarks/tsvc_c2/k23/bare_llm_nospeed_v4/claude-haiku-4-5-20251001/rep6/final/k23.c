#include "data.h"

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(u, v, w, c, x, d) schedule(static)
        for (long i = 1; i < LEN_1D; i++) {
            u[i] += w[i] * c[i];
            v[i] = x[i] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
