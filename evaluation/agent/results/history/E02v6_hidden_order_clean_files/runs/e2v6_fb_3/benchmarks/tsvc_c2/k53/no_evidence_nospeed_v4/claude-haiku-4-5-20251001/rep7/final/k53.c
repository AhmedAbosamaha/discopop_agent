#include "data.h"
#include <stdlib.h>

real_t kernel_k53(void)
{
    real_t *u_work = (real_t *)malloc(sizeof(real_t) * LEN_1D);
    real_t *v_work = (real_t *)malloc(sizeof(real_t) * LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(v_work,u_work) 
        for (long i = 0; i < LEN_1D; i++) {
            u_work[i] = u[i];
            v_work[i] = v[i];
        }
        for (long i = 1; i < LEN_1D; i++) {
            u_work[ju[i]] += v_work[kv[i]] * c[i];
            v_work[jv[i]] = u_work[ku[i]] * d[i] + c[i];
        }
        #pragma omp parallel for shared(v_work,u_work) 
        for (long i = 0; i < LEN_1D; i++) {
            u[i] = u_work[i];
            v[i] = v_work[i];
        }
        dummy(a, b, c, d, e);
    }

    free(u_work);
    free(v_work);
    return (real_t)0;
}
