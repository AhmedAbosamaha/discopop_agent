#include "data.h"
#include <stdlib.h>

real_t kernel_k53(void)
{
    real_t *u_temp = (real_t*)malloc(LEN_1D * sizeof(real_t));
    real_t *v_temp = (real_t*)malloc(LEN_1D * sizeof(real_t));

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(u_temp,v_temp) 
        for (long i = 0; i < LEN_1D; i++) {
            u_temp[i] = u[i];
            v_temp[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u_temp[ju[i]] += v_temp[kv[i]] * c[i];
            v_temp[jv[i]] = u_temp[ku[i]] * d[i] + c[i];
        }
        #pragma omp parallel for shared(u_temp,v_temp) 
        for (long i = 0; i < LEN_1D; i++) {
            u[i] = u_temp[i];
            v[i] = v_temp[i];
        }
        dummy(a, b, c, d, e);
    }

    free(u_temp);
    free(v_temp);
    return (real_t)0;
}
