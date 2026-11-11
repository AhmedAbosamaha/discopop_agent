#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_local = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *v_local = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *w_local = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(u_local, u, LEN_1D * sizeof(real_t));
        memcpy(v_local, v, LEN_1D * sizeof(real_t));
        memcpy(w_local, w, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_local[ju[i]] += w_local[kw[i]] * c[i];
            v_local[jv[i]] = u_local[ku[i]] * d[i] + c[i];
            w_local[jw[i]] = v_local[kv[i]] * e[i] + d[i];
        }

        memcpy(u, u_local, LEN_1D * sizeof(real_t));
        memcpy(v, v_local, LEN_1D * sizeof(real_t));
        memcpy(w, w_local, LEN_1D * sizeof(real_t));
        free(u_local);
        free(v_local);
        free(w_local);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
