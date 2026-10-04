#include "data.h"

real_t kernel_k48(void)
{
    for (long i = 1; i < LEN_1D; i++) {
        u[ju[i]] += v[kv[i]] * c[i];
        v[jv[i]] = u[ku[i]] * d[i] + c[i];
    }
    return (real_t)0;
}
