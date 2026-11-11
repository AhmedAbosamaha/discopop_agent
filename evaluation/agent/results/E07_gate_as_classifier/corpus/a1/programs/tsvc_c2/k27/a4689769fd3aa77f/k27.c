#include <stdlib.h>
#include <string.h>
#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *w_work = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *v_work = (real_t *)malloc(LEN_1D * sizeof(real_t));

        memcpy(w_work, w, LEN_1D * sizeof(real_t));
        memcpy(v_work, v, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w_work[kw[i]] * c[i];
            v_work[jv[i]] = u[ku[i]] * d[i] + c[i];
            w_work[jw[i]] = v_work[kv[i]] * e[i] + d[i];
        }

        memcpy(w, w_work, LEN_1D * sizeof(real_t));
        memcpy(v, v_work, LEN_1D * sizeof(real_t));

        free(w_work);
        free(v_work);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
