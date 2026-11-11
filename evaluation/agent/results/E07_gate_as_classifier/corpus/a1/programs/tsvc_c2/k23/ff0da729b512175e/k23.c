#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k23(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *w_buf = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *c_buf = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *d_buf = (real_t *)malloc(LEN_1D * sizeof(real_t));

        memcpy(w_buf, w, LEN_1D * sizeof(real_t));
        memcpy(c_buf, c, LEN_1D * sizeof(real_t));
        memcpy(d_buf, d, LEN_1D * sizeof(real_t));

        for (long i = 1; i < LEN_1D; i++) {
            u[i] += w_buf[i] * c_buf[i];
            v[i] = x[i] * d_buf[i] + c_buf[i];
        }

        free(w_buf);
        free(c_buf);
        free(d_buf);

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
