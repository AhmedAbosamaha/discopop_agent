#include "data.h"
#include <stdlib.h>

real_t kernel_k27(void)
{
    real_t *u_local = (real_t *)malloc(LEN_1D * sizeof(real_t));
    real_t *v_local = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            u_local[i] = u[i];
            v_local[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u_local[ju[i]] += w[kw[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v_local[jv[i]] = u_local[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v_local[kv[i]] * e[i] + d[i];
        }
        for (long i = 0; i < LEN_1D; i++) {
            u[i] = u_local[i];
            v[i] = v_local[i];
        }
        dummy(a, b, c, d, e);
    }
    free(u_local);
    free(v_local);
    return (real_t)0;
}
