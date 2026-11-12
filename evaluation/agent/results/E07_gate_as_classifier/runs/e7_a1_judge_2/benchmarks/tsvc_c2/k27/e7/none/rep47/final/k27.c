#include "data.h"
#include <stdlib.h>

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_cache = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *v_cache = (real_t *)malloc(LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w[kw[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u_cache[i] = u[ku[i]];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u_cache[i] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v_cache[i] = v[kv[i]];
        }
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v_cache[i] * e[i] + d[i];
        }

        free(u_cache);
        free(v_cache);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
