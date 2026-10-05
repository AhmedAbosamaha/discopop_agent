#include "data.h"
#include <stdlib.h>

real_t kernel_s1213(void)
{
    /*
     * Original recurrence per sweep (fixed nl):
     *   a[i] = b[i-1] + c[i]      // uses b[i-1] just written by iteration i-1
     *   b[i] = a[i+1] * d[i]      // uses a[i+1], NOT yet written (i+1 comes later)
     *
     * So b[i] always reads the pre-sweep value of a[i+1]. Unrolling the
     * a[i] <- b[i-1] chain shows a[i] (for i>=2) also only ever depends on
     * the pre-sweep value of a[i] itself (A[i]):
     *   b[i-1] = A[i] * d[i-1]   =>   a[i] = A[i]*d[i-1] + c[i]   (i>=2)
     *   a[1]   = b[0] + c[1]                                      (b[0] never written)
     *   b[i]   = A[i+1] * d[i]                                    (1<=i<=LEN_1D-2)
     *
     * So the only loop-carried dependence is through the pre-sweep snapshot
     * of a[]. We materialize that snapshot once per sweep (a_old), then every
     * iteration i reads only a_old[] (never a[], which it itself is about to
     * overwrite) and writes exclusively to a[i] and b[i] -- disjoint
     * locations across iterations, so the main loop is race-free in any order.
     * a_old is heap-allocated since LEN_1D can be very large.
     */
    real_t *a_old = (real_t *)malloc(sizeof(real_t) * (size_t)LEN_1D);

    for (int nl = 0; nl < iterations; nl++) {
        #pragma omp parallel for shared(a, a_old) schedule(static)
        for (int i = 0; i < LEN_1D; i++) {
            a_old[i] = a[i];
        }

        #pragma omp parallel for shared(a, a_old, b, c, d) schedule(static)
        for (int i = 1; i < LEN_1D-1; i++) {
            if (i == 1) {
                a[1] = b[0] + c[1];
            } else {
                a[i] = a_old[i]*d[i-1] + c[i];
            }
            b[i] = a_old[i+1]*d[i];
        }
        dummy(a, b, c, d, e);
    }

    free(a_old);
    return (real_t)0;
}
