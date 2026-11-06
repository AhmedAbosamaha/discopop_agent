#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // First pass: compute all v values
        #pragma omp parallel for shared(v, u, ku, d, c, jv)
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }

        // Second pass: compute all w values
        #pragma omp parallel for shared(w, v, kv, e, d, jw)
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v[kv[i]] * e[i] + d[i];
        }

        // Third pass: update all u values
        #pragma omp parallel for shared(u, w, kw, c, ju)
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w[kw[i]] * c[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
