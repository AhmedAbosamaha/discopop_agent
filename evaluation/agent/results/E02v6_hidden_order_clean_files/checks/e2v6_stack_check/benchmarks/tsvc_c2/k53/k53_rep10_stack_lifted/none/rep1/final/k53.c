#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t u_snapshot[LEN_1D], c_snapshot[LEN_1D], d_snapshot[LEN_1D];
        for (long i = 0; i < LEN_1D; i++) {
            u_snapshot[i] = u[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            c_snapshot[i] = c[i];
            d_snapshot[i] = d[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u_snapshot[ju[i]] += v[kv[i]] * c_snapshot[i];
            v[jv[i]] = u_snapshot[ku[i]] * d_snapshot[i] + c_snapshot[i];
        }
        #pragma omp parallel for firstprivate(u_snapshot) 
        for (long i = 0; i < LEN_1D; i++) {
            u[i] = u_snapshot[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
