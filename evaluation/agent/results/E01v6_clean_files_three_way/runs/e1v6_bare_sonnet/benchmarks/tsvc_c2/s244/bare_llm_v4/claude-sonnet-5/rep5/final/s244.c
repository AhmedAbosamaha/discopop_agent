#include "data.h"

real_t kernel_s244(void)
{
    for (int nl = 0; nl < iterations; nl++) {
        /* Original recurrence:
         *   a[i]   = b[i] + c[i]*d[i]
         *   b[i]   = c[i] + b[i]
         *   a[i+1] = b[i] + a[i+1]*d[i]
         * The write to a[i+1] made here is always overwritten by the next
         * iteration's a[i] write, except at the very last index
         * (i = LEN_1D-2), where a[LEN_1D-1] survives untouched by the loop.
         * So the elementwise part (a[i], b[i] for i < LEN_1D-1) is fully
         * independent across i; only the final element a[LEN_1D-1] needs
         * to be computed after the loop, using the updated b[LEN_1D-2]
         * and the original (loop-untouched) a[LEN_1D-1].
         */
        #pragma omp parallel for shared(a, b, c, d) schedule(static)
        for (int i = 0; i < LEN_1D-1; ++i) {
            real_t b_orig = b[i];
            a[i] = b_orig + c[i] * d[i];
            b[i] = c[i] + b_orig;
        }
        if (LEN_1D >= 2) {
            a[LEN_1D-1] = b[LEN_1D-2] + a[LEN_1D-1] * d[LEN_1D-2];
        }
        dummy(a, b, c, d, e);
    }
    return (real_t)0;
}
