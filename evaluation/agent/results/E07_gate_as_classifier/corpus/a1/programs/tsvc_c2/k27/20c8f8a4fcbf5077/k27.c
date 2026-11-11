#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_new = malloc(LEN_1D * sizeof(real_t));
        memcpy(u_new, u, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_new[ju[i]] += w[kw[i]] * c[i];
            v[jv[i]] = u_new[ku[i]] * d[i] + c[i];
            w[jw[i]] = v[kv[i]] * e[i] + d[i];
        }

        memcpy(u, u_new, LEN_1D * sizeof(real_t));
        free(u_new);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
