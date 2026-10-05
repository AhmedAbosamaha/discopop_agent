#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* The original loop writes a[i+1] on iteration i, but that write
         * is always overwritten by iteration i+1's own a[i+1] = b[i+1] +
         * c[i+1]*d[i+1] computation (line 1 of the next iteration), except
         * for i+1 == LEN_1D-1, which no later iteration touches.  So the
         * cross-iteration write to a[i+1] is dead everywhere but the last
         * element.  Removing it leaves each i independent: a[i] and b[i]
         * only read/write index i.  The last element is then fixed up once,
         * after the parallel loop's implicit barrier, using the freshly
         * updated b[LEN_1D-2] (matching the value the sequential version
         * would have seen at that point) and the still-untouched original
         * a[LEN_1D-1].
         */
        int n = LEN_1D - 1;
        #pragma omp parallel for shared(a, b, c, d) schedule(static)
        for (int i = 0; i < n; ++i) {
            a[i] = b[i] + c[i] * d[i];
            b[i] = c[i] + b[i];
        }
        a[n] = b[n-1] + a[n] * d[n-1];
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
