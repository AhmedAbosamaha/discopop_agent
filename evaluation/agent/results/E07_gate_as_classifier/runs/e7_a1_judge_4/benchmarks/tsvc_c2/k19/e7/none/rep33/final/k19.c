#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k19(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Buffer u updates to separate accumulation from reads
        real_t *u_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(u_new, u, LEN_1D * sizeof(real_t));

        // Loop: read v live (updated by earlier iterations), buffer u, update v in-place
        for (long i = 1; i < LEN_1D; i++) {
            u_new[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u_new[ku[i]] * d[i] + c[i];
        }

        // Apply buffered u updates
        memcpy(u, u_new, LEN_1D * sizeof(real_t));

        free(u_new);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
