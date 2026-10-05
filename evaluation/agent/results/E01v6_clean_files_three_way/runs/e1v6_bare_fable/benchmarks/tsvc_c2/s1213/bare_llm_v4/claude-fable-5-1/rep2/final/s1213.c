#include "data.h"

real_t kernel_s1213(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Original: a[i] = b[i-1]+c[i]; b[i] = a[i+1]*d[i].
         * The read of a[i+1] always sees the old a (anti-dependence),
         * so all of b can be computed first; a[i] then reads the new
         * b[i-1] (and the untouched b[0]) exactly as the serial order did. */
#pragma omp parallel for default(none) shared(a, b, d) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }
#pragma omp parallel for default(none) shared(a, b, c) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
