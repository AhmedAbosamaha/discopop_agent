#include "data.h"

real_t kernel_k27(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        double* v_old = (double*)malloc(sizeof(double) * LEN_1D);
        memcpy(v_old, v, sizeof(double) * LEN_1D);

        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = v_old[kv[i]] * e[i] + d[i];
            v[jv[i]] = u[ku[i]] * d[i] + c[i];
        }

        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += w[kw[i]] * c[i];
        }

        free(v_old);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
