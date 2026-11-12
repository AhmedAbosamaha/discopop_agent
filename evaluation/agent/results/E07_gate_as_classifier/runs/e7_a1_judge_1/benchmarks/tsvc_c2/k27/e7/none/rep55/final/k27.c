#include "data.h"
#include <string.h>

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t u_local[LEN_1D], v_local[LEN_1D], w_local[LEN_1D];
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
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
