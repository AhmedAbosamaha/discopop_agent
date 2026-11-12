#include "data.h"
#include <stdlib.h>

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Compute all v values first (based on current u)
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }

        // Phase 2: Update all u values (reading newly updated v from phase 1)
        #pragma omp parallel for 
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
