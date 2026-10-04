#include "data.h"

real_t kernel_vas(int * __restrict__ ip)
{
    #pragma omp parallel for shared(ip) 
    for (int i = 0; i < LEN_1D; i++) {
        a[ip[i]] = b[i];
    }
    return (real_t)0;
}
