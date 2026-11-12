#include "data.h"

real_t kernel_k53(void)
{
    real_t *v_snapshot = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    real_t *v_new = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        // Phase 1: Snapshot v values that will be read
        for (long i = 1; i < LEN_1D; i++) {
            v_snapshot[i] = v[kv[i]];
        }

        // Phase 2: Update u using snapshot of v (no loop-carried dependence on v)
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_snapshot[i] * c[i];
        }

        // Phase 3: Compute new v values using updated u
        for (long i = 1; i < LEN_1D; i++) {
            v_new[i] = u[ku[i]] * d[i] + c[i];
        }

        // Phase 4: Write new v values
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = v_new[i];
        }

        dummy(a, b, c, d, e);
    }

    free(v_snapshot);
    free(v_new);
    return (real_t)0;
}
