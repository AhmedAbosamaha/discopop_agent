#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_work = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *v_input = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *c_input = (real_t *)malloc(LEN_1D * sizeof(real_t));
        memcpy(u_work, u, LEN_1D * sizeof(real_t));
        memcpy(v_input, v, LEN_1D * sizeof(real_t));
        memcpy(c_input, c, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u_work[ju[i]] += v_input[kv[i]] * c_input[i];
            v[jv[i]] = u_work[ku[i]] * d[i] + c_input[i];
        }

        memcpy(u, u_work, LEN_1D * sizeof(real_t));
        free(u_work);
        free(v_input);
        free(c_input);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
