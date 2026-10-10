#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t v_work[LEN_1D];
        for (long k = 0; k < LEN_1D; k++) {
            v_work[k] = v[k];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_work[kv[i]] * c[i];
            v_work[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        #pragma omp parallel for firstprivate(v_work) 
        for (long k = 0; k < LEN_1D; k++) {
            v[k] = v_work[k];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
