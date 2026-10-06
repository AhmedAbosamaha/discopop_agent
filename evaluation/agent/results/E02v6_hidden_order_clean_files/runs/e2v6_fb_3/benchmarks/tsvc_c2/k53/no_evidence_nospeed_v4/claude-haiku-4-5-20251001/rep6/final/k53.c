#include <stdlib.h>
#include "data.h"

real_t kernel_k53(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        real_t* u_temp = (real_t*)malloc(sizeof(real_t) * LEN_1D);
        #pragma omp parallel for shared(u_temp) 
        for (long i = 0; i < LEN_1D; i++) {
            u_temp[i] = u[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u_temp[ju[i]] += v[kv[i]] * c[i];
            v[jv[i]] = u_temp[ku[i]] * d[i] + c[i];
        }
        #pragma omp parallel for shared(u_temp) 
        for (long i = 0; i < LEN_1D; i++) {
            u[i] = u_temp[i];
        }
        free(u_temp);
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
