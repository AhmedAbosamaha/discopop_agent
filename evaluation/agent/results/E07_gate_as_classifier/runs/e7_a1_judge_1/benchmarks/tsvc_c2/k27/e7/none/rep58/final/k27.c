#include "data.h"
#include <stdlib.h>

real_t kernel_k27(void)
{
    real_t *v_saved = (real_t *)malloc(LEN_1D * sizeof(real_t));
    // Initialize v_saved from v's initial state before first nl
    for (long i = 0; i < LEN_1D; i++) {
        v_saved[i] = v[i];
    }
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v_saved[kv[i]] * e[i] + d[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w[kw[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        // Save v at end of nl for next nl to use
        for (long i = 0; i < LEN_1D; i++) {
            v_saved[i] = v[i];
        }
        dummy(a, b, c, d, e);
    }
    free(v_saved);
    return (real_t)0;
}
