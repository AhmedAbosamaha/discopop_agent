#include "data.h"
#include <stdlib.h>

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *temp_u = (real_t *)malloc(LEN_1D * sizeof(real_t));

        // Phase 1: Save u values needed for v updates (gather before modifications)
        #pragma omp parallel for shared(temp_u, u, ku)
        for (long i = 1; i < LEN_1D; i++) {
            temp_u[i] = u[ku[i]];
        }

        // Phase 2: Update v using saved u values (scatter operation)
        #pragma omp parallel for shared(v, jv, temp_u, d, c)
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = temp_u[i] * d[i] + c[i];
        }

        // Phase 3: Update u using current v values (atomic for += conflicts)
        #pragma omp parallel for shared(u, ju, v, kv, c)
        for (long i = 1; i < LEN_1D; i++) {
            real_t val = v[kv[i]] * c[i];
            #pragma omp atomic
            u[ju[i]] += val;
        }

        free(temp_u);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
