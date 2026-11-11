#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k27(void)
{
    real_t* w_old = (real_t*)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        memcpy(w_old, w, LEN_1D * sizeof(real_t));
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w_old[kw[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v[kv[i]] * e[i] + d[i];
        }
        dummy(a, b, c, d, e);
    }
    free(w_old);
    return (real_t)0;
}
