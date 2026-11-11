#include "data.h"
#include <stdlib.h>

real_t kernel_k53(void)
{
    real_t *vtemp = (real_t *)malloc(LEN_1D * sizeof(real_t));
    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v[kv[i]] * c[i];
            vtemp[i] = u[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = vtemp[i];
        }
        dummy(a, b, c, d, e);
    }
    free(vtemp);
    return (real_t)0;
}
