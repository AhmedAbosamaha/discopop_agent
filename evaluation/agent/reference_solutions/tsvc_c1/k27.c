#include "data.h"

real_t kernel_k27(void)
{
    #pragma omp parallel for
    for (long i = 1; i < LEN_1D; i++) v[jv[i]] = u[ku[i]] * d[i] + c[i];
    #pragma omp parallel for
    for (long i = 1; i < LEN_1D; i++) w[jw[i]] = v[kv[i]] * e[i] + d[i];
    #pragma omp parallel for
    for (long i = 1; i < LEN_1D; i++) u[ju[i]] += w[kw[i]] * c[i];
    return (real_t)0;
}
