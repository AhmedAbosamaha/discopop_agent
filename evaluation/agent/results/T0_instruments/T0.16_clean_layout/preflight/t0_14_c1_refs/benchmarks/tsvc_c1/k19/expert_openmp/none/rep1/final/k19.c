#include "data.h"

real_t kernel_k19(void)
{
    #pragma omp parallel for
    for (long i = 1; i < LEN_1D; i++) v[jv[i]] = u[ku[i]] * d[i] + c[i];
    #pragma omp parallel for
    for (long i = 1; i < LEN_1D; i++) u[ju[i]] += v[kv[i]] * c[i];
    return (real_t)0;
}
