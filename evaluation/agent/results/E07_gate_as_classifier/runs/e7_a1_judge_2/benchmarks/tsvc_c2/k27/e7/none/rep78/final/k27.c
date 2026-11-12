#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k27(void)
{
    real_t *u_tmp = (real_t*)malloc(LEN_1D * sizeof(real_t));
    real_t *v_tmp = (real_t*)malloc(LEN_1D * sizeof(real_t));
    real_t *w_tmp = (real_t*)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memcpy(u_tmp, u, LEN_1D * sizeof(real_t));
        for (long i = 1; i < LEN_1D; i++) {
            u_tmp[ju[i]] += w[kw[i]] * c[i];
        }
        memcpy(u, u_tmp, LEN_1D * sizeof(real_t));

        memcpy(v_tmp, v, LEN_1D * sizeof(real_t));
        for (long i = 1; i < LEN_1D; i++) {
            v_tmp[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        memcpy(v, v_tmp, LEN_1D * sizeof(real_t));

        memcpy(w_tmp, w, LEN_1D * sizeof(real_t));
        for (long i = 1; i < LEN_1D; i++) {
            w_tmp[jw[i]] = v[kv[i]] * e[i] + d[i];
        }
        memcpy(w, w_tmp, LEN_1D * sizeof(real_t));

        dummy(a, b, c, d, e);
    }

    free(u_tmp);
    free(v_tmp);
    free(w_tmp);
    return (real_t)0;
}
