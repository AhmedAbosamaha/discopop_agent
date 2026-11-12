#include "data.h"
#include <stdlib.h>

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *v_new = (real_t *)malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(v_new) 
        for (long i = 0; i < LEN_1D; i++) {
            v_new[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u[ju[i]] += v_new[kv[i]] * c[i];
            v_new[jv[i]] = u[ku[i]] * d[i] + c[i];
        }
        #pragma omp parallel for shared(v_new) 
        for (long i = 0; i < LEN_1D; i++) {
            v[i] = v_new[i];
        }
        free(v_new);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
