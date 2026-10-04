#include "data.h"

real_t kernel_s000(void)
{
    #pragma omp parallel for schedule(static) default(none) shared(a, b)
    for (int i = 0; i < LEN_1D; i++) {
        a[i] = b[i] + 1;
    }
    return (real_t)0;
}
