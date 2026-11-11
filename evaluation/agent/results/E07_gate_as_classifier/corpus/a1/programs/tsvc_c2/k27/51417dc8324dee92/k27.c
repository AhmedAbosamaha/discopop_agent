#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Pass 1: Compute v (break RAW from v writes to v reads)
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        // Pass 2: Compute w (v is now fully available)
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v[kv[i]] * e[i] + d[i];
        }
        // Pass 3: Compute u (w is now fully available)
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w[kw[i]] * c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
