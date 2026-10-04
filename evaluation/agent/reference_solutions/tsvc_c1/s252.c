#include "data.h"

real_t kernel_s252(void)
{
    #pragma omp parallel for
    for (int i = 0; i < LEN_1D; i++) {
        real_t s = b[i] * c[i];
        real_t t = (i > 0) ? b[i-1] * c[i-1] : (real_t) 0.;
        a[i] = s + t;
    }
    return (real_t)0;
}
