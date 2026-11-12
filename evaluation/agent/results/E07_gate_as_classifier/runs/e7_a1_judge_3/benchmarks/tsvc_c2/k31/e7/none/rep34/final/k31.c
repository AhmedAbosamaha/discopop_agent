#include "data.h"
#include <stdlib.h>
#include <string.h>

real_t kernel_k31(void)
{
    if (far > 0) {
        real_t *u_old = malloc(LEN_1D * sizeof(real_t));
        for (int nl = 0; nl < iterations; nl++) {
            memcpy(u_old, u, LEN_1D * sizeof(real_t));
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
            }
            for (long i = 1; i < LEN_1D; i++) {
                v[i] = u_old[i + far] * d[i] + c[i];
            }
            dummy(a, b, c, d, e);
        }
        free(u_old);
    } else {
        for (int nl = 0; nl < iterations; nl++) {
            for (long i = 1; i < LEN_1D; i++) {
                u[i] += v[i + off] * c[i];
            }
            for (long i = 1; i < LEN_1D; i++) {
                v[i] = u[i + far] * d[i] + c[i];
            }
            dummy(a, b, c, d, e);
        }
    }
    return (real_t)0;
}
