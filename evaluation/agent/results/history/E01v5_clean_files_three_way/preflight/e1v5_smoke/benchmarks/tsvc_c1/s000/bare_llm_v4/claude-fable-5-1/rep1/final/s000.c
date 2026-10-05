#include "data.h"

real_t kernel_s000(void)
{
    /* Each iteration writes only a[i] and reads only b[i]; a and b are
       distinct global arrays, so iterations are independent. */
#pragma omp parallel for default(none) shared(a, b) schedule(static)
    for (int i = 0; i < LEN_1D; i++) {
        a[i] = b[i] + 1;
    }
    return (real_t)0;
}
