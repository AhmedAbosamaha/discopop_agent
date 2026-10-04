#include <stdlib.h>
#include "data.h"

real_t kernel_s481(void)
{
    #pragma omp parallel for 
    for (int i = 0; i < LEN_1D; i++) {
        if (d[i] < (real_t)0.) {
            exit (0);
        }
        a[i] += b[i] * c[i];
    }
    return (real_t)0;
}
