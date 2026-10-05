#include "data.h"

real_t kernel_s000(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Each iteration touches only a[i] and b[i]: no cross-iteration
         * dependence.  The outer nl loop stays sequential because dummy()
         * mutates a and b between activations. */
#pragma omp parallel for default(none) shared(a, b) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            a[i] = b[i] + 1;
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
