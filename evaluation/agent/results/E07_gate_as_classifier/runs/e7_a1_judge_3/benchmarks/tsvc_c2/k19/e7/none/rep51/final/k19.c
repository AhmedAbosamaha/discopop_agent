#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Buffer v updates to decouple write dependencies
        real_t *v_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(v_new, v, LEN_1D * sizeof(real_t));

        // Loop reads from live u and v as they are updated
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            v_new[jv[i]] = u[ku[i]] * d[i] + c[i];
        }

        // Apply buffered v updates after all u updates are visible
        memcpy(v, v_new, LEN_1D * sizeof(real_t));

        free(v_new);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
