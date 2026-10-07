#include <stdlib.h>
#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t *u_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
        real_t *v_temp = (real_t *)malloc(LEN_1D * sizeof(real_t));
        #pragma omp parallel for shared(v_temp,u_temp) 
        for (long i = 0; i < LEN_1D; i++) {
            u_temp[i] = u[i];
            v_temp[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u_temp[ju[i]] += v_temp[kv[i]] * c[i];
            v_temp[jv[i]] = u_temp[ku[i]] * d[i] + c[i];
        }
        #pragma omp parallel for shared(v_temp,u_temp) 
        for (long i = 0; i < LEN_1D; i++) {
            u[i] = u_temp[i];
            v[i] = v_temp[i];
        }
        free(u_temp);
        free(v_temp);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
