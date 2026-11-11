#include "data.h"

real_t kernel_k27(void)
{
    real_t *w_snapshot = malloc(LEN_1D * sizeof(real_t));
    memcpy(w_snapshot, w, LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w_snapshot[kw[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v[kv[i]] * e[i] + d[i];
        }
        memcpy(w_snapshot, w, LEN_1D * sizeof(real_t));
        dummy(a, b, c, d, e);
    }

    free(w_snapshot);
    return (real_t)0;
}
