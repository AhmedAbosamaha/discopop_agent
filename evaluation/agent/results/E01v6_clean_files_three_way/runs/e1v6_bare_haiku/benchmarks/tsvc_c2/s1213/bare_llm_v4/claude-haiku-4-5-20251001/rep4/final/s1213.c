#include "data.h"

real_t kernel_s1213(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        // Loop A: Compute all a[i] values in parallel
        // Each iteration i reads b[i-1] and c[i] (no loop-carried dep on b since b is not written here)
        // Each iteration i writes to a[i] (no conflicts since different elements written)
        #pragma omp parallel for shared(a, b, c) private(i)
        for (int i = 1; i < LEN_1D-1; i++) {
            a[i] = b[i-1]+c[i];
        }

        // Loop B: Compute all b[i] values in parallel
        // Each iteration i reads a[i+1] and d[i] (a was updated by Loop A, but each i reads different a[i+1])
        // Each iteration i writes to b[i] (no conflicts since different elements written)
        #pragma omp parallel for shared(a, b, d) private(i)
        for (int i = 1; i < LEN_1D-1; i++) {
            b[i] = a[i+1]*d[i];
        }

        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
