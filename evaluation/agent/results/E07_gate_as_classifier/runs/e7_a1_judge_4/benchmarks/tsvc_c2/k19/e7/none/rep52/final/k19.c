#include "data.h"

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* u_delta = (real_t*)calloc(LEN_1D, sizeof(real_t));
        real_t* v_new = (real_t*)malloc(LEN_1D * sizeof(real_t));

        // Phase 1: Accumulate updates to u (no loop-carried dependencies)
        for (long i = 1; i < LEN_1D; i++) {
            u_delta[ju[i]] += v[kv[i]] * c[i];
        }

        // Phase 2: Apply accumulated updates to u
        for (long idx = 0; idx < LEN_1D; idx++) {
            u[idx] += u_delta[idx];
        }

        // Phase 3: Compute new v values (reads updated u)
        for (long i = 1; i < LEN_1D; i++) {
            v_new[jv[i]] = u[ku[i]] * d[i] + c[i];
        }

        // Phase 4: Apply v updates
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = v_new[jv[i]];
        }

        free(u_delta);
        free(v_new);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
