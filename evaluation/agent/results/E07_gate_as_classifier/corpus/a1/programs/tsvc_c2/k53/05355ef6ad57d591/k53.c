#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_work = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(u_work, u, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_work[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u_work[ku[i]] * d[i] + c[i];
        }

        memcpy(u, u_work, LEN_1D * sizeof(real_t));
        free(u_work);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
