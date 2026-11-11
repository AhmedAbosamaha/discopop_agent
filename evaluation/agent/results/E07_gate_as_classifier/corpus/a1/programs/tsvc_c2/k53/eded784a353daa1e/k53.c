#include "data.h"
#include <string.h>

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t v_new[LEN_1D];
        memcpy(v_new, v, sizeof(real_t) * LEN_1D);
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_new[kv[i]] * c[i];
            v_new[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        memcpy(v, v_new, sizeof(real_t) * LEN_1D);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
