#include <stdlib.h>
#include <string.h>
#include "data.h"

real_t kernel_k27(void)
{
    real_t *u_incr = (real_t *)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        memset(u_incr, 0, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_incr[ju[i]] += w[kw[i]] * c[i];
            v[jv[i]] = (u[ku[i]] + u_incr[ku[i]]) * d[i] + c[i];
            w[jw[i]] = v[kv[i]] * e[i] + d[i];
        }

        for (long j = 1; j < LEN_1D; j++) {
            u[j] += u_incr[j];
        }

        dummy(a, b, c, d, e);
    }

    free(u_incr);
    return (real_t)0;
}
