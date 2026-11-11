#include "data.h"

real_t kernel_k27(void)
{
    real_t *u_temp = malloc(LEN_1D * sizeof(real_t));
    real_t *v_temp = malloc(LEN_1D * sizeof(real_t));
    real_t *w_temp = malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        for (long i = 1; i < LEN_1D; i++) {
            u_temp[i] = w[kw[i]] * c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += u_temp[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v_temp[i] = u[ku[i]] * d[i] + c[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            v[jv[i]] = v_temp[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            w_temp[i] = v[kv[i]] * e[i] + d[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            w[jw[i]] = w_temp[i];
        }
        dummy(a, b, c, d, e);
    }

    free(u_temp);
    free(v_temp);
    free(w_temp);

    return (real_t)0;
}
