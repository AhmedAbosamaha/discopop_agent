#include "data.h"

real_t kernel_k42(void)
{
    #pragma omp parallel for
    for (long i = 1; i < LEN_1D; i++) u[ju[i]] += v[kv[i]] * c[i];
    #pragma omp parallel for
    for (long i = 1; i < LEN_1D; i++) v[jv[i]] += u[ku[i]] * d[i];
    return (real_t)0;
}
