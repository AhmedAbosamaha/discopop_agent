#include "data.h"
#include <stdlib.h>

real_t kernel_k27(void)
{
    real_t *v_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 0; i < LEN_1D; i++) {
            v_temp[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v_temp[kv[i]] * e[i] + d[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w[kw[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        dummy(a, b, c, d, e);
    }
    free(v_temp);
    return (real_t)0;
}
