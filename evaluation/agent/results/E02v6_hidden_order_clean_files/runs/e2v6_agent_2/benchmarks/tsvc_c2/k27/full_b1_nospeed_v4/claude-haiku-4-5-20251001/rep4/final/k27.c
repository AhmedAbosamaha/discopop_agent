#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: compute all v values
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        // Phase 2: compute all w values using v from phase 1
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v[kv[i]] * e[i] + d[i];
        }
        // Phase 3: compute all u values using w from phase 2
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w[kw[i]] * c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
